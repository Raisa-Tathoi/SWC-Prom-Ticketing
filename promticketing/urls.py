"""
URL configuration for promticketing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from registration.views import book_tickets, mark_as_paid, index, success, qr_code_scan

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('book/', book_tickets, name='book_tickets'),
    path('mark_as_paid/<int:booking_id>/', mark_as_paid, name='mark_as_paid'),
    path('success/', success, name='success'),
    path('booking/<int:booking_id>/', qr_code_scan, name='qr_code_scan'),
    path('payment_due/<int:booking_id>/', qr_code_scan, name='payment_due'),
]
