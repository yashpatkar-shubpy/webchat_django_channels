from django.urls import path
from .views import home, room, ConversationCreateAPIView

urlpatterns = [
    path('', home),
    path('conversation/', ConversationCreateAPIView.as_view()),
    path('<str:room_name>/room/', room)
]