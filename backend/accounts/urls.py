from django.urls import path
from .views import Signup, Login, Logout, signup_page, login_page


urlpatterns = [
    path('signup/', signup_page, name='signup_page'),
    path('login/', login_page, name='login_page'),
    path('api/signup/',  Signup.as_view()),
    path('api/login/',  Login.as_view()),
    path('api/logout/', Logout.as_view()),
]