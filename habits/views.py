from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Habit
from .paginators import HabitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций с привычками."""
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Свои привычки + публичные"""
        user = self.request.user
        return Habit.objects.filter(user=user) | Habit.objects.filter(is_public=True)

    def perform_create(self, serializer):
        """При создании привычки привязываем текущего пользователя"""
        serializer.save(user=self.request.user)