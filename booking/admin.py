from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from booking.models import CustomUser, Cylinder, Booking, ChatMessage


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_staff', 'is_active', 'is_delivery')
    list_filter = ('is_staff', 'is_active', 'is_delivery')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_delivery')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'is_delivery'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(Cylinder)
class CylinderAdmin(admin.ModelAdmin):
    list_display = ('type', 'stock')
    search_fields = ('type',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'cylinder_type', 'preferred_delivery_date', 'status', 'payment_status', 'created_at', 'delivery_person')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('user__email', 'cylinder_type__type', 'delivery_address')
    date_hierarchy = 'created_at'
    actions = ['mark_as_confirmed']

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='Confirmed')
        self.message_user(request, f'{updated} booking(s) marked as Confirmed.')

    mark_as_confirmed.short_description = 'Mark selected bookings as Confirmed'

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['booking', 'sender', 'message', 'timestamp']
    list_filter = ['booking', 'sender']
    search_fields = ['message']

admin.site.register(ChatMessage, ChatMessageAdmin)