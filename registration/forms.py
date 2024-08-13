from django import forms
from django.core.exceptions import ValidationError
from .models import Booking

class BookingForm(forms.ModelForm):
    send_copy_to_guests = forms.BooleanField(required=False, label="Send a copy to guests")
    confirm_information = forms.BooleanField(required=True, label="Confirm information")

    class Meta:
        model = Booking
        fields = ['name', 'phone_number', 'school_email', 'number_of_tickets']

    def clean_school_email(self):
        email = self.cleaned_data.get('school_email')
        if not email.endswith('@educbe.ca'):
            raise ValidationError("Please enter a valid CBE email address ending with @educbe.ca.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        number_of_tickets = cleaned_data.get('number_of_tickets')
        if number_of_tickets:
            for i in range(1, number_of_tickets):
                guest_email = self.data.get(f'guest_email_{i}')
                if guest_email and not guest_email.endswith('@educbe.ca'):
                    self.add_error(f'guest_email_{i}', "Please enter a valid CBE email address ending with @educbe.ca.")
        return cleaned_data