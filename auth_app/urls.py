from django.urls import path
from .views import register, request_otp, verify_otp

urlpatterns = [
    path('register/', register),
    path('request-otp/', request_otp),
    path('verify-otp/', verify_otp),
]
