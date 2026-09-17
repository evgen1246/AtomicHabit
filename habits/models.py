from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class HabitsModel(models.Model):
    "Модель привычки"

    habit_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="habits",
        help_text="Создатель привычки",
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку",
    )
    date_time = models.TimeField(
        verbose_name="Время", help_text="Время, когда необходимо выполнять привычку"
    )
    action = models.CharField(
        max_length=255,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка",
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Приятная привычка",
        help_text="Признак приятной привычки (True) или полезной (False)",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Связанная привычка",
        related_name="related_habits",
        help_text="Привычка, которая связана с другой привычкой (только для полезных)",
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность (в днях)",
        help_text="Периодичность выполнения привычки для напоминания в днях",
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Чем пользователь должен себя вознаградить после выполнения",
    )

    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение (в секундах)",
        help_text="Время, которое пользователь потратит на выполнение привычки (не более 120 секунд)",
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
        help_text="Привычки можно публиковать в общий доступ",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.place}"
