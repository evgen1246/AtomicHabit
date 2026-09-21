from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычки"""

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, attrs):
        """Валидация на уровне сериализатора"""
        related_habit = attrs.get("related_habit")
        reward = attrs.get("reward")
        duration = attrs.get("duration")
        is_pleasant = attrs.get("is_pleasant")
        periodicity = attrs.get("periodicity")

        if related_habit and reward:
            raise serializers.ValidationError(
                "Нельзя одновременно указывать связанную привычку и вознаграждение."
            )

        if duration and duration > 120:
            raise serializers.ValidationError(
                "Время на выполнение не может превышать 120 секунд."
            )

        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "Связанная привычка должна быть приятной."
            )

        if is_pleasant:
            if reward:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения."
                )
            if related_habit:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть связанной привычки."
                )

        if periodicity:
            if periodicity < 1:
                raise serializers.ValidationError(
                    "Периодичность должна быть не менее 1 дня."
                )
            elif periodicity > 7:
                raise serializers.ValidationError(
                    "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
                )

        return attrs