from django.core.mail import send_mail
from django.conf import settings


def send_email(sender, email, conversation_id):
    subject = "Chat APP"
    message = (
        f"user: {sender} wants to chat with you. \n "
        f"Accept Link: http://127.0.0.1:8000/chat/accept/{conversation_id}/ \n"
        f"Reject Link: http://127.0.0.1:8000/chat/reject/{conversation_id}/"
    )
    sender = settings.EMAIL_HOST_USER
    recipients = [email]

    response = send_mail(subject, message, sender, recipients)
    return response