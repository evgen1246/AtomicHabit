from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Habit
from .paginators import HabitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.filter(habit_creator=user) | Habit.objects.filter(
            is_public=True
        )

    def perform_create(self, serializer):
        serializer.save(habit_creator=self.request.user)
