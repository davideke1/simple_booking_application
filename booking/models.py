from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _

from .manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_active = models.BooleanField(_('active'), default=False)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_delivery = models.BooleanField(_('delivery driver'), default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def email_user(self,subject,message,**kwargs):
        from_email= settings.EMAIL_BACKEND
        send_mail(subject,message,from_email,[self.email],**kwargs)

    @staticmethod
    def total_delivery_personnel():
        return CustomUser.objects.filter(is_delivery=True).count()

class Cylinder(models.Model):
    type = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.type} ({self.stock})"

    def update_stock(self, amount):
        self.stock = F('stock') + amount
        self.save()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Assigned', 'Assigned'),
        ('In_Transit', 'In_Transit'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cylinder_type = models.ForeignKey(Cylinder, on_delete=models.CASCADE)
    preferred_delivery_date = models.DateField()
    delivery_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_person = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to=Q(is_delivery=True),related_name='deliveries')

    def mark_as_confirmed(self):
            self.status = 'Confirmed'
            self.save()


    @staticmethod
    def total_bookings():
        return Booking.objects.count()

    @staticmethod
    def total_confirmed_bookings():
        return Booking.objects.filter(status='Confirmed').count()

    @staticmethod
    def total_deliveries():
        return Booking.objects.filter(status='Delivered').count()


class ChatMessage(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)