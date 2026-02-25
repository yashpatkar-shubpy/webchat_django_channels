from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from .serializers import SignupSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import render
from django.contrib.auth import login, logout


User = get_user_model()

class Signup(CreateAPIView):
    serializer_class = SignupSerializer

class Login(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        login(request, user)

        return Response(
            {'email': user.email},
            status=status.HTTP_200_OK
        )
    
class Logout(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})

def signup_page(request):
    return render(request, "signup.html")

def login_page(request):
    return render(request, "login.html")
