from celery import shared_task
from .services.send_email import send_email


@shared_task
def send_invite_email(sender, email, room_id):
    return send_email(sender, email, room_id)
