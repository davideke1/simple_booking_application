import json

import requests
import stripe
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string, get_template
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa

from .forms import CustomUserCreationForm, UserLoginForm, BookingForm, AssignDeliveryForm, CylinderForm, \
    UpdateDeliveryStatusForm
from .models import CustomUser, Booking, Cylinder, ChatMessage

stripe.api_key = settings.STRIPE_SECRET_KEY
def homepage(request):
    return render(request,'booking/homepage.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until it is confirmed
            user.save()
            # Send activation email
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('registration/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('registration_success')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def registration_success(request):
    return render(request, 'registration/registration_success.html')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. You can now log in to your account.')
    else:
        return HttpResponse('Activation link is invalid!')
from django.shortcuts import render

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_dashboard')
                elif user.is_delivery:
                    return redirect('delivery-dashboard')
                else:
                    return redirect('user-dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin-dashboard')
    elif request.user.is_delivery:
        return redirect('delivery-dashboard')
    else:
        return redirect('user-dashboard')

@user_passes_test(lambda u: u.is_staff)
def assign_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    delivery_persons = CustomUser.objects.filter(is_delivery_driver=True)

    if request.method == 'POST':
        delivery_person_id = request.POST.get('delivery_person')
        delivery_person = get_object_or_404(CustomUser, id=delivery_person_id)
        booking.delivery_person = delivery_person
        booking.status = 'Assigned'
        booking.save()

        # Notify the delivery person (for simplicity, we'll use a JSON response)
        # You can extend this to send emails or use Django Channels for real-time notifications
        return JsonResponse({'message': f'Booking {booking.id} assigned to {delivery_person.email}'})

    return render(request, 'booking/admin/assign_booking.html', {
        'booking': booking,
        'delivery_persons': delivery_persons,
    })

@login_required
def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/users/dashboard.html', {'bookings': bookings})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    context = {
        'total_bookings': Booking.total_bookings(),
        'total_confirmed_bookings': Booking.total_confirmed_bookings(),
        'total_deliveries': Booking.total_deliveries(),
        'total_delivery_personnel': CustomUser.total_delivery_personnel(),
    }

    return render(request, 'booking/admin/dashboard.html', context)

# @login_required
# def generate_invoice(request, booking_id):
#     # if not request.user.is_staff:
#     #     return redirect('home')
#
#     booking = get_object_or_404(Booking, id=booking_id)
#     template_path = 'booking/admin/invoice.html'
#     context = {'booking': booking}
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="invoice_{booking_id}.pdf"'
#     template = get_template(template_path)
#     html = template.render(context)
#
#     pisa_status = pisa.CreatePDF(html, dest=response)
#     if pisa_status.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response


def send_email_notification(subject, message, recipient_list):
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def send_sms_notification(phone_number, message):
    payload = {
        'apikey': settings.SMS_API_KEY,
        'numbers': phone_number,
        'message': message,
        'sender': 'TXTLCL'
    }
    response = requests.post(settings.SMS_API_URL, data=payload)
    return response.status_code

@login_required
def generate_reports(request):
    if not request.user.is_staff:
        return redirect('home')

    bookings = Booking.objects.all()

    context = {
        'bookings': bookings
    }

    return render(request, 'booking/admin/reports.html', context)


@login_required
def delivery_management(request):
    if not request.user.is_staff:
        return redirect('home')

    bookings = Booking.objects.filter(status__in=['Confirmed', 'Assigned']).order_by('-created_at')
    delivery_personnel = CustomUser.objects.filter(is_delivery=True)

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        delivery_person_id = request.POST.get('delivery_person')
        booking = get_object_or_404(Booking, id=booking_id)
        delivery_person = get_object_or_404(CustomUser, id=delivery_person_id)
        booking.delivery_person = delivery_person
        if booking.status == 'Confirmed':
            booking.status = 'Assigned'
        booking.save()

        send_mail(
            'Delivery Assignment',
            f'You have been assigned to a new delivery (Booking ID: {booking.id}).',
            'from@example.com',
            [delivery_person.email],
            fail_silently=False,
        )

        message = f'Booking {booking.id} assigned to {delivery_person.email}' if booking.status == 'Assigned' else f'Delivery person updated for booking {booking.id}'
        return JsonResponse({'message': message})

    context = {
        'bookings': bookings,
        'delivery_personnel': delivery_personnel,
    }
    return render(request, 'booking/admin/deliveries.html', context)

@login_required
def inventory_management(request):
    if not request.user.is_staff:
        return redirect('home')

    cylinders = Cylinder.objects.all()

    if request.method == 'POST':
        form = CylinderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_management')
    else:
        form = CylinderForm()

    context = {
        'cylinders': cylinders,
        'form': form
    }

    return render(request, 'booking/admin/inventory.html', context)

@login_required
def delivery_dashboard(request):
    deliveries = Booking.objects.filter(
        Q(status='Assigned', delivery_person=request.user) | Q(status='In_Transit', delivery_person=request.user)
    )

    return render(request, 'booking/delivery/dashboard.html', {'deliveries': deliveries})

@login_required
def update_delivery_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = UpdateDeliveryStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('delivery-dashboard')
    else:
        form = UpdateDeliveryStatusForm(instance=booking)
    return render(request, 'booking/delivery/update_delivery_status.html', {'form': form})

@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, status__in=['Assigned', 'In_Transit'])
    if request.user == booking.user or request.user == booking.delivery_person:
        messages = ChatMessage.objects.filter(booking=booking).order_by('timestamp')
        return render(request, 'booking/delivery/chat.html', {'booking': booking, 'messages': messages})
    else:
        return redirect('home')


class CreateBookingView(LoginRequiredMixin, View):
    def get(self, request):
        form = BookingForm()
        return render(request, 'booking/users/create_booking.html', {'form': form})

    def post(self, request):
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect('booking_status', booking_id=booking.id)
        return render(request, 'booking/users/create_booking.html', {'form': form})

class BookingHistoryView(LoginRequiredMixin, View):
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        return render(request, 'booking/users/booking_history.html', {'bookings': bookings})

class BookingStatusView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id, user=request.user)
        messages = ChatMessage.objects.filter(booking=booking).order_by('timestamp')
        return render(request, 'booking/users/booking_status.html', {'booking': booking, 'messages':messages})

class PaymentView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id, user=request.user)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Cylinder Booking',
                    },
                    'unit_amount': 2000,  # $20.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/booking_status/{booking_id}/'),
            cancel_url=request.build_absolute_uri(f'/booking_status/{booking_id}/'),
        )
        booking.payment_status = 'Pending'
        booking.save()
        return redirect(session.url, code=303)

class InitiatePaymentView(LoginRequiredMixin,View):
    def get(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id, user=request.user)
        return render(request, 'booking/users/initiate_payment.html', {
            'booking': booking,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })

class PaymentSuccessView(LoginRequiredMixin,View):
    def get(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id, user=request.user)
        booking.payment_status = 'Completed'
        booking.mark_as_confirmed()
        booking.save()
        return render(request, 'booking/users/payment_success.html', {'booking': booking})

#
@login_required
def generate_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    template_path = 'booking/admin/invoice.html'
    context = {'booking': booking}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="invoice_for_booking_id{booking_id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
#

class PaymentCancelView(LoginRequiredMixin,View):
    def get(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id, user=request.user)
        booking.payment_status = 'Failed'
        booking.save()
        return render(request, 'booking/users/payment_cancel.html', {'booking': booking})

import logging

logger = logging.getLogger(__name__)

@require_POST
def create_checkout_session(request):
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        if not booking_id:
            return JsonResponse({'error': 'Booking ID not provided'}, status=400)

        booking = Booking.objects.get(id=booking_id)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Gas Booking',
                    },
                    'unit_amount': 2000,  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://127.0.0.1:8000/payment/success/{booking.id}/',
            cancel_url=f'http://127.0.0.1:8000/payment/cancel/{booking.id}/',
        )
        return JsonResponse({'id': session.id})
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)