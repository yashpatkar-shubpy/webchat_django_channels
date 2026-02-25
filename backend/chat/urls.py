from django.urls import path
from .views import home, room, ListPrivateUsersAPIView, ListGroupUsersAPIView, PrivateConversationAPIView, GroupConversationAPIView, AcceptConversationAPIView, RejectConversationAPIView, ListChatHistoryAPIView

urlpatterns = [
    path('', home, name='home'),
    path('private/', PrivateConversationAPIView.as_view()),
    path('group/', GroupConversationAPIView.as_view()),
    path('<uuid:conversation_id>/', room, name='room'),
    path("accept/<uuid:conversation_id>/", AcceptConversationAPIView.as_view()),
    path("reject/<uuid:conversation_id>/", RejectConversationAPIView.as_view()),
    path('private-users/', ListPrivateUsersAPIView.as_view()),
    path('group-users/', ListGroupUsersAPIView.as_view()),
    path('history-chats/', ListChatHistoryAPIView.as_view()),
]