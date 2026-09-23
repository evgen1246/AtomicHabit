from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import Habit
from .services import TelegramService


@shared_task
def send_habit_reminder(habit_id: int):
    """Отправляет напоминание о привычке пользователю в Telegram"""
    try:
        habit = Habit.objects.select_related("user").get(id=habit_id)
    except Habit.DoesNotExist:
        return f"Привычка {habit_id} не найдена"

    user = habit.user

    if not user.telegram_id:
        return f"У пользователя {user.email} нет Telegram ID"

    text = (
        f"🔔 <b>Напоминание о привычке</b>\n\n"
        f"⏰ Время: {habit.time}\n"
        f"📍 Место: {habit.place}\n"
        f"🎯 Действие: {habit.action}\n"
    )

    if habit.duration:
        text += f"⏱ Время на выполнение: {habit.duration} сек\n"

    if habit.reward:
        text += f"🎁 Вознаграждение: {habit.reward}\n"

    if habit.related_habit:
        text += f"🔗 Связанная привычка: {habit.related_habit.action}\n"

    result = TelegramService.send_message(user.telegram_id, text)

    if result.get("ok"):
        return f"Напоминание отправлено: {user.email}"
    return f"Ошибка: {result.get('error')}"


@shared_task
def send_all_habit_reminders():
    """Каждый час проверяет привычки, время которых наступило,и отправляет напоминания."""
    now = timezone.now()
    current_hour = now.hour
    current_minute = now.minute
    habits = Habit.objects.filter(
        time__hour=current_hour,
        time__minute=current_minute,
    ).select_related("user")

    sent_count = 0
    for habit in habits:
        if habit.user.telegram_id:
            send_habit_reminder.delay(habit.id)
            sent_count += 1

    return f"Отправлено напоминаний: {sent_count}"