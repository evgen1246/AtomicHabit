from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserRegistrationSerializer


class RegisterAPIView(CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "message": "Пользователь успешно зарегистрирован",
            },
            status=status.HTTP_201_CREATED,
        )


class TelegramLinkView(APIView):
    """Привязка Telegram ID к профилю пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        telegram_id = request.data.get("telegram_id")

        if not telegram_id:
            return Response(
                {"error": "Не указан telegram_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.telegram_id = telegram_id
        user.save(update_fields=["telegram_id"])

        return Response(
            {
                "message": "Telegram ID успешно привязан",
                "telegram_id": telegram_id,
            },
            status=status.HTTP_200_OK,
        )