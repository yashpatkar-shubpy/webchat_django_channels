from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from .serializers import SignupSerializer, LoginSerializer, UserSerializer, ConversationSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import render
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from chat.models import Conversation


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

class UserList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # --- Private conversations ---
        private_conversations = (
            Conversation.objects
            .filter(type="private", members=request.user)
            .prefetch_related("members")
        )

        private_user_ids = set()

        for conv in private_conversations:
            for member in conv.members.all():
                if member.id != request.user.id:
                    private_user_ids.add(member.id)

        # --- 1-1 Chat Users (filtered) ---
        private_chat_users = (
            User.objects
            .exclude(id=request.user.id)
            .exclude(id__in=private_user_ids)
        )

        # --- Group Chat Users (all except self) ---
        group_chat_users = (
            User.objects
            .exclude(id=request.user.id)
        )

        # --- Conversations ---
        conversations = (
            Conversation.objects
            .filter(members=request.user)
            .prefetch_related("members")
            .order_by("-created_at")
        )

        return Response({
            "private_users": UserSerializer(private_chat_users, many=True).data,
            "group_users": UserSerializer(group_chat_users, many=True).data,
            "chat_history": ConversationSerializer(
                conversations,
                many=True,
                context={"request": request}
            ).data
        })