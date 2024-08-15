from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File

class Booking(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    school_email = models.EmailField()
    number_of_tickets = models.PositiveIntegerField()
    payment_due = models.FloatField(editable=False, default=0)
    payment_qr_code = models.ImageField(upload_to='payment_qr_codes', blank=True, null=True)
    booking_qr_code = models.ImageField(upload_to='booking_qr_codes', blank=True, null=True)
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate payment QR code
        if not self.payment_qr_code:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(f'https://swc-prom-ticketing.onrender.com/payment_due/{self.id}')
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f'payment_qr_code_{self.id}.png'
            self.payment_qr_code.save(file_name, File(buffer), save=False)

        # Generate booking QR code if paid
        if self.paid and not self.booking_qr_code:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(f'https://swc-prom-ticketing.onrender.com/booking_details/{self.id}')
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f'booking_qr_code_{self.id}.png'
            self.booking_qr_code.save(file_name, File(buffer), save=False)

        if self.number_of_tickets % 2 == 0:
            pending = self.number_of_tickets * 5
        else:
            pending = self.number_of_tickets * 7
        self.payment_due = pending

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Guest(models.Model):
    booking = models.ForeignKey(Booking, related_name='guests', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f'{self.booking.name} - {self.name}'
