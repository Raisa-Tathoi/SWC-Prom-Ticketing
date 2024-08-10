# Generated by Django 4.2.15 on 2024-08-10 04:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('school_email', models.EmailField(max_length=254)),
                ('number_of_tickets', models.PositiveIntegerField()),
                ('alert_phone_number', models.CharField(max_length=15)),
                ('payment_due', models.FloatField(default=0, editable=False)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes')),
                ('paid', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guests', to='registration.booking')),
            ],
        ),
    ]
