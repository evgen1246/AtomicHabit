from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .apps import UsersConfig
from .views import CustomTokenObtainPairView, RegisterAPIView, TelegramLinkView

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("telegram/link/", TelegramLinkView.as_view(), name="telegram_link"),
]
