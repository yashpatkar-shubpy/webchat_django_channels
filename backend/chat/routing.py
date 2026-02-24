from django.urls import re_path
from .consumer import Chatting

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", Chatting.as_asgi()),
]