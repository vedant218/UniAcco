from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP
from .serializers import UserSerializer, OTPSerializer
from django.utils import timezone
from datetime import timedelta

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            return Response({"message": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=email, email=email)
        user.save()
        return Response({"message": "Registration successful. Please verify your email."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def request_otp(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        otp, created = OTP.objects.get_or_create(user=user)
        if not created:
            otp.created_at = timezone.now()
            otp.save()
        # Mock sending OTP via email
        print(f"OTP for {email}: {otp.otp}")
        return Response({"message": "OTP sent to your email."})
    except User.DoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp_input = request.data.get('otp')
    try:
        user = User.objects.get(email=email)
        otp = OTP.objects.get(user=user, otp=otp_input)
        if otp.created_at + timedelta(minutes=5) < timezone.now():
            return Response({"message": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        otp.delete()
        return Response({"message": "Login successful.", "token": str(refresh.access_token)})
    except (User.DoesNotExist, OTP.DoesNotExist):
        return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
