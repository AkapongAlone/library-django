from django.urls import path
from user.views import RegisterView, UserListAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view()),
    path('users', UserListAPIView.as_view() ),
 ]