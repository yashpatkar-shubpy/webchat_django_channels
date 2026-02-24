from services.room_name import generate_room_name
from django.contrib.auth import get_user_model
from chat.models import Conversation
from chat.tasks import send_invite_email
from rest_framework import status

User = get_user_model()

def conversation_service(type, creator, *member_ids):

    # check the type = private and no. of members
    if type == 'private' and len(*member_ids) == 1:
        type = 'private'
        member_not_exists_id = set()
        member_exists_email = set()

        member_id = member_ids[0]
        member = User.objects.filter(id=member_id).first()

        if not member:
            member_not_exists_id.add(member)
        member_exists_email.add(member.email)
    

    elif type == 'group' and len(*member_ids) >= 2:
        type='group'
        member_not_exists_id = set()
        member_exists_email = set()

        for member_id in member_ids:
            member = User.objects.filter(id=member_id).first()

            if not member:
                member_not_exists_id.add(member)
            member_exists_email.add(member.email)


    # ----------------same for both types-----------------
    # creating roomname
    room_name = generate_room_name()

    # check room already exists
    conversation = Conversation.objects.filter(
        name=room_name,
    ).first()
    
    if conversation and type == "private":
        if member_exists_email[0] in conversation.members.email:
            return{"message": "member already exists", "room_name": room_name, "non_exists_user": None, "status":status.HTTP_200_OK}
        
    elif conversation and type == "group":
        for email in conversation.members.email:
            member_exists_email.remove(email)
            if len(member_exists_email) == 0:    
                return{"message": "member already exists", "room_name": room_name, "non_exists_user": None, "status":status.HTTP_200_OK}

    # Create conversation
    conversation = Conversation.objects.create(type=type, name=room_name)
    conversation.members(creator)
    for mem_id in member_ids:
        # get object of each member
        user = User.objects.filter(id=mem_id).first()
        conversation.member.add(user)
    conversation.save()

    # Send email
    for member_email in member_exists_email:
        send_invite_email.delay(creator.email, member_email, room_name)

    return{"message":"email sent","room_name": room_name, "non_exists_user": list(member_not_exists_id), "status":status.HTTP_201_CREATED}