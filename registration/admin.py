from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, Guest

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

admin.site.register(Booking, BookingAdmin)
