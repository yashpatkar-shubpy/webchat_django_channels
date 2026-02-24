from django.core.mail import send_mail
from django.conf import settings


def send_email(sender, email, roomname):
    subject = "Chat APP"
    message = f"user: {sender} wants to chat with you. Link: http://127.0.0.1:8000/chat/{roomname}/room/"
    sender = settings.EMAIL_HOST_USER
    recipients = [email]

    response = send_mail(subject, message, sender, recipients)
    return response 