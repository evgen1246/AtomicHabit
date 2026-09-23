from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import RegisterAPIView, TelegramLinkView

app_name = "users"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("telegram/link/", TelegramLinkView.as_view(), name="telegram_link"),
]