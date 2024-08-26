from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.conf import settings
from registration.models import Booking, Guest
from registration.views import generate_qr_code

class GuestInline(admin.TabularInline):
    model = Guest
    extra = 1

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_details', 'guests', 'payment_due', 'paid')
    inlines = [GuestInline]
    list_filter = ('paid',)
    list_editable = ('paid',)

    def booking_details(self, obj):
        return f"{obj.name} - {obj.school_email}"
    booking_details.short_description = 'Booking Details'

    def guests(self, obj):
        guests = obj.guests.all()
        guest_details = "<br>".join(
            [f"{guest.name} ({guest.email})" for guest in guests]
        )
        return format_html(guest_details)
    guests.short_description = 'Guests'

    def save_model(self, request, obj, form, change):
        # Check if the 'paid' status is being changed to True
        if obj.pk and form.has_changed() and 'paid' in form.changed_data and obj.paid:
            # Send the booking details email
            self.send_booking_details_email(obj)
        super().save_model(request, obj, form, change)


    def send_booking_details_email(self, booking):
        email_recipients = [booking.school_email] + [guest.email for guest in booking.guests.all()]
        booking_details_email = EmailMessage(
            'Your Booking Details',
            'Please find your booking details QR code attached. Show this to the volunteer at the entrance to redeem your ticket. BE SURE TO BRING YOUR SCHOOL ID OR A PICTURE IDENTIFICATION WITH YOU!!',
            settings.DEFAULT_FROM_EMAIL,
            email_recipients
        )

        # Generate QR code for booking details
        booking_qr_code = generate_qr_code(f'https://swc-prom-ticketing.onrender.com/booking_details/{booking.id}')
        booking.booking_qr_code.save(f'booking_qr_code_{booking.id}.png', booking_qr_code, save=False)
        booking.save()  # Save QR code path to model

        booking_details_email.attach_file(booking.booking_qr_code.path)
        booking_details_email.send()


admin.site.register(Booking, BookingAdmin)