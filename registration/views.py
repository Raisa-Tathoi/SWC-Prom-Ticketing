from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from .forms import BookingForm
from .models import Booking, Guest
import qrcode
from io import BytesIO
from django.core.files import File
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging


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

            # Generate QR code for payment_due
            payment_qr_code = generate_qr_code(f'https://swc-prom-ticketing.onrender.com/payment_due/{booking.id}')
            booking.payment_qr_code.save(f'payment_qr_code_{booking.id}.png', payment_qr_code, save=False)
            booking.save()  # Save QR code path to model

            # Initial email with payment_due QR code
            email_recipients = [booking.school_email] + guest_emails
            initial_email = EmailMessage(
                'Your Payment QR Code',
                'The QR below, when scanned takes you to a page that displays the total amount that you have to pay for your tickets. Please show this at the booth when purchasing your tickets.',
                settings.DEFAULT_FROM_EMAIL,
                email_recipients
            )
            initial_email.attach_file(booking.payment_qr_code.path)
            initial_email.send()

            return redirect('success')
        else:
            return render(request, 'booking/book_tickets.html', {'form': form})

    else:
        form = BookingForm()

    return render(request, 'booking/book_tickets.html', {'form': form})


logger = logging.getLogger(__name__)

@csrf_exempt
def update_booking_paid_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            paid = data.get('paid')

            if booking_id is None or paid is None:
                logger.error("Missing booking_id or paid field in the request")
                return JsonResponse({'status': 'error', 'message': 'Missing booking_id or paid field'})

            booking = Booking.objects.get(id=booking_id)
            booking.paid = paid
            booking.save()

            logger.info(f"Booking ID {booking_id} updated to {'paid' if paid else 'not paid'}")
            return JsonResponse({'status': 'success'})
        except Booking.DoesNotExist:
            logger.error(f"Booking ID {booking_id} not found")
            return JsonResponse({'status': 'error', 'message': 'Booking not found'})
        except json.JSONDecodeError:
            logger.error("Invalid JSON data")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return File(buffer, name=f'qr_code_{url.split("/")[-1]}.png')


def success(request):
    return render(request, 'booking/success.html')


def index(request):
    return render(request, 'booking/index.html')


def qr_code_scan(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.paid:
        guests = booking.guests.all()
        return render(request, 'booking/booking_details.html', {'booking': booking, 'guests': guests})
    else:
        return render(request, 'booking/payment_due.html', {'payment_due': booking.payment_due})
