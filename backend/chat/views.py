from django.shortcuts import render, redirect
from rest_framework.generics import GenericAPIView, ListAPIView
from django.contrib.auth import get_user_model
from .models import Conversation, Message, ChatInvite
from rest_framework.response import Response
from rest_framework import status
from chat.tasks import send_invite_email
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .serializers import GroupSerializer, PrivateSerializer, UserSerializer, ChatHistorySerializer
from django.db.models import Count

User = get_user_model()

class GroupConversationAPIView(GenericAPIView):
    '''used for logic of group member adding into db'''
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_name = serializer.validated_data["group_name"]
        member_ids = serializer.validated_data["member_ids"]

        conversation = Conversation.objects.create(
            type=Conversation.Type.GROUP,
            name=group_name,
            created_by=request.user,
        )

        # Add creator immediately
        conversation.members.add(request.user)

        for member_id in member_ids:
            member = User.objects.get(id=member_id)

            ChatInvite.objects.create(
                conversation=conversation,
                sender=request.user,
                receiver=member,
            )

            send_invite_email.delay(
                request.user.email,
                member.email,
                str(conversation.id)
            )

        return Response(
            {"conversation_id": conversation.id},
            status=status.HTTP_201_CREATED
        )
    
class PrivateConversationAPIView(GenericAPIView):
    '''used for logic of private room member adding into db'''
    permission_classes = [IsAuthenticated]
    serializer_class = PrivateSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        receiver_id = serializer.validated_data["member_id"]
        receiver = User.objects.get(id=receiver_id)
        
        conversation = (
            Conversation.objects
            .filter(type=Conversation.Type.PRIVATE)
            .annotate(member_count=Count("members"))
            .filter(member_count=2)
            .filter(members=request.user)
            .filter(members=receiver)
            .first()
        )

        if conversation:
            return Response(
                {"conversation_id": conversation.id},
                status=status.HTTP_200_OK
            )

        conversation = Conversation.objects.create(
            type=Conversation.Type.PRIVATE,
            created_by=request.user,
        )

        invite = (
            ChatInvite.objects
            .filter(
                sender=request.user,
                receiver=receiver,
                status=ChatInvite.Status.PENDING,
                conversation__type=Conversation.Type.PRIVATE
            )
            .select_related("conversation")
            .first()
        )

        if invite:
            return Response({"conversation_id": invite.conversation.id})

        conversation.members.add(request.user)

        ChatInvite.objects.create(conversation=conversation, sender=request.user, receiver=receiver, status=ChatInvite.Status.PENDING)

        send_invite_email.delay(request.user.email, receiver.email, str(conversation.id))

        return Response(
            {"conversation_id": conversation.id},
            status=status.HTTP_201_CREATED
        )

class AcceptConversationAPIView(GenericAPIView):
    '''runs when user click url link from the email'''
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request, conversation_id):

        invite = (
            ChatInvite.objects
            .select_related("conversation")
            .filter(
                conversation_id=conversation_id,
                receiver=request.user
            )
            .first()
        )

        if not invite:
            return Response(
                {"message": "Invite not found."},
                status=status.HTTP_403_FORBIDDEN
            )

        # If already accepted
        if invite.status == ChatInvite.Status.ACCEPTED:
            return redirect("room", conversation_id=invite.conversation.id)

        # Accept invite
        invite.status = ChatInvite.Status.ACCEPTED
        invite.save(update_fields=["status"])

        invite.conversation.members.add(request.user)

        return redirect("room", conversation_id=invite.conversation.id)
    
class RejectConversationAPIView(GenericAPIView):
    '''runs when user click url link from the email for reject'''
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request, conversation_id):

        invite = (
            ChatInvite.objects
            .select_related("conversation")
            .filter(
                conversation_id=conversation_id,
                receiver=request.user
            )
            .first()
        )

        if not invite:
            return Response(
                {"message": "Invite not found."},
                status=status.HTTP_403_FORBIDDEN
            )

        if invite.status != ChatInvite.Status.PENDING:
            return HttpResponse("Invite already processed.")

        invite.status = ChatInvite.Status.REJECTED
        invite.save(update_fields=["status"])

        # Delete private conversation entirely
        if invite.conversation.type == Conversation.Type.PRIVATE:
            invite.conversation.delete()
            print('chat deleted')

        return redirect("home")

def home(request):
    if not request.user.is_authenticated:
        return redirect('login_page')
    
    return render(request, 'home.html')

def room(request, conversation_id):
    if not request.user.is_authenticated:
        return redirect('login_page')
    
    conversation = Conversation.objects.filter(id=conversation_id).first()
    if not conversation:
        return HttpResponse("Not allowed.")
    
    if not conversation.members.filter(id=request.user.id).exists():
        return HttpResponse("Not allowed.")

    messages = Message.objects.filter(
        conversation=conversation
    ).order_by("created_at")

    return render(request, 'room.html', {
        'conversation_id': conversation_id,
        "user_email": request.user.email,
        "messages": messages
    })

class ListPrivateUsersAPIView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)

class ListGroupUsersAPIView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)

class ListChatHistoryAPIView(ListAPIView):
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(members=self.request.user)
            .only("id", "type", "created_at")
            .order_by("-updated_at")
        )