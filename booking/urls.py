from django.urls import path
from . import views
from .views import CreateBookingView, BookingStatusView, BookingHistoryView, InitiatePaymentView, PaymentSuccessView, \
    PaymentCancelView, create_checkout_session, admin_dashboard, inventory_management, delivery_management, \
    generate_reports, generate_invoice

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('booking/create/', views.create_booking, name='create-booking'),
    # path('booking/payment/<int:booking_id>/', views.process_payment, name='process-payment'),
    # path('admin-view/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/assign-booking/<int:booking_id>/', views.assign_booking, name='assign-booking'),
    path('user/dashboard/', views.user_dashboard, name='user-dashboard'),
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery-dashboard'),
    path('delivery/update-status/<int:booking_id>/', views.update_delivery_status, name='update-delivery-status'),
    path('chat/<int:booking_id>/', views.chat_view, name='chat_view'),
    path('create_booking/', CreateBookingView.as_view(), name='create_booking'),
    path('booking_history/', BookingHistoryView.as_view(), name='booking_history'),
    path('booking_status/<int:booking_id>/', BookingStatusView.as_view(), name='booking_status'),
    path('payment/<int:booking_id>/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment/success/<int:booking_id>/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/cancel/<int:booking_id>/', PaymentCancelView.as_view(), name='payment_cancel'),
    # path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),

    path('admin-view/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-view/inventory/', inventory_management, name='inventory_management'),
    path('admin-view/delivery/', delivery_management, name='delivery_management'),
    path('admin-view/reports/', generate_reports, name='generate_reports'),
    path('admin-view/invoice/<int:booking_id>/', generate_invoice, name='generate_invoice'),
]



