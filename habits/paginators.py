from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """Пагинатор для привычек: 5 на страницу"""

    default_limit = 5
    max_limit = 50
