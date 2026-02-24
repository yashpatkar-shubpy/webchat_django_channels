from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from rest_framework.response import Response
from rest_framework import status
from chat.tasks import send_invite_email
from django.http import HttpResponse
from .serializers import ConversationCreateSerializer

User = get_user_model()

class ConversationCreateAPIView(CreateAPIView):
    serializer_class = ConversationCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_type = serializer.validated_data["type"]
        member_ids = serializer.validated_data["member_ids"]
        creator = request.user

        members = []

        for member_id in member_ids:
            user = User.objects.filter(id=member_id).first()
            if not user:
                return Response(
                    {"detail": f"User {member_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            members.append(user)

        all_member_ids = sorted(member_ids + [creator.id])
        room_name = "chat"
        for member_id in all_member_ids:
            room_name+="_" + str(member_id)

        # Check if conversation already exists
        conversation = Conversation.objects.filter(
            name=room_name
        ).first()

        if conversation:
            return Response(
                {"room_name": room_name},
                status=status.HTTP_200_OK
            )

        # Create conversation
        conversation = Conversation.objects.create(
            type=conversation_type,
            name=room_name
        )

        conversation.members.add(creator, *members)

        # Send emails
        for member in members:
            send_invite_email.delay(
                creator.email,
                member.email,
                room_name
            )

        return Response(
            {"room_name": room_name},
            status=status.HTTP_201_CREATED
        )


def home(request):
    return render(request, 'home.html')

def room(request, room_name):
    conversation = Conversation.objects.filter(name=room_name).first()
    if not conversation:
        return HttpResponse("Not allowed.")
    
    if not conversation.members.filter(id=request.user.id).exists():
        return HttpResponse("Not allowed.")

    messages = Message.objects.filter(
        conversation=conversation
    ).order_by("created_at")

    return render(request, 'room.html', {
        'roomname': room_name,
        "user_email": request.user.email,
        "messages": messages
    })