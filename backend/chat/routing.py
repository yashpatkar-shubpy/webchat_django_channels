from django.urls import path
from .consumer import Chatting

websocket_urlpatterns = [
    path("ws/chat/<uuid:conversation_id>/", Chatting.as_asgi()),
]