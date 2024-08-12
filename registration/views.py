from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from .forms import BookingForm
from .models import Booking, Guest

def book_tickets(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()

            number_of_tickets = form.cleaned_data.get('number_of_tickets')
            send_copy_to_guests = form.cleaned_data.get('send_copy_to_guests')

            guest_emails = []
            for i in range(1, number_of_tickets):
                guest_name = request.POST.get(f'guest_name_{i}')
                guest_email = request.POST.get(f'guest_email_{i}')
                if guest_name and guest_email:
                    Guest.objects.create(booking=booking, name=guest_name, email=guest_email)
                    if send_copy_to_guests:
                        guest_emails.append(guest_email)

            if send_copy_to_guests:
                email_recipients = [booking.school_email] + guest_emails
            else:
                email_recipients = [booking.school_email]

            email = EmailMessage(
                'Your Booking QR Code',
                'Please find your QR code attached.',
                settings.DEFAULT_FROM_EMAIL,
                email_recipients
            )
            email.attach_file(booking.qr_code.path)
            email.send()

            return redirect('success')
        else:
            return render(request, 'booking/book_tickets.html', {'form': form})

    else:
        form = BookingForm()

    return render(request, 'booking/book_tickets.html', {'form': form})

def success(request):
    return render(request, 'booking/success.html')

def index(request):
    return render(request, 'booking/index.html')

def qr_code_scan(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.paid:
        guests = booking.guests.all()
        return render(request, 'booking_details.html', {'booking': booking, 'guests': guests})
    else:
        return render(request, 'payment_due.html', {'payment_due': booking.payment_due})
