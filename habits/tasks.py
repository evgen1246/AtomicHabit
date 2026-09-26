from celery import shared_task
from django.utils import timezone

from .models import Habit
from .services import TelegramService


@shared_task
def send_habit_reminder(habit_id: int) -> str:
    try:
        habit = Habit.objects.select_related(
            "habit_creator",
            "related_habit",
        ).get(pk=habit_id)
    except Habit.DoesNotExist:
        return f"Привычка {habit_id} не найдена"

    user = habit.habit_creator
    if not user.telegram_id:
        return f"У пользователя {user.email} нет Telegram ID"

    text = (
        "🔔 <b>Напоминание о привычке</b>\n\n"
        f"⏰ Время: {habit.date_time}\n"
        f"📍 Место: {habit.place}\n"
        f"🎯 Действие: {habit.action}\n"
        f"⏱ Время на выполнение: {habit.duration} сек\n"
    )

    if habit.reward:
        text += f"🎁 Вознаграждение: {habit.reward}\n"

    if habit.related_habit:
        text += (
            "🔗 Связанная привычка: "
            f"{habit.related_habit.action}\n"
        )

    result = TelegramService.send_message(
        user.telegram_id,
        text,
    )

    if result.get("ok"):
        habit.last_reminded_at = timezone.now()
        habit.save(update_fields=("last_reminded_at",))
        return f"Напоминание отправлено: {user.email}"

    return f"Ошибка: {result.get('error')}"


@shared_task
def send_all_habit_reminders() -> str:
    now = timezone.localtime()
    habits = Habit.objects.filter(
        date_time__hour=now.hour,
        date_time__minute=now.minute,
    ).select_related("habit_creator")

    sent_count = 0

    for habit in habits:
        if not habit.habit_creator.telegram_id:
            continue

        if habit.last_reminded_at is not None:
            last_date = timezone.localtime(
                habit.last_reminded_at
            ).date()
            days_passed = (now.date() - last_date).days

            if days_passed < habit.periodicity:
                continue

        send_habit_reminder.delay(habit.pk)
        sent_count += 1

    return f"Отправлено напоминаний: {sent_count}"
@shared_task
def send_all_habit_reminders():
    """Каждую минуту проверяет привычки, время которых наступило"""
    now = timezone.now()
    current_time = now.time()
    habits = Habit.objects.filter(
        date_time__hour=current_time.hour,
        date_time__minute=current_time.minute,
    ).select_related("habit_creator")

    sent_count = 0
    for habit in habits:
        if habit.habit_creator.telegram_id:
            send_habit_reminder.delay(habit.id)
            sent_count += 1

    return f"Отправлено напоминаний: {sent_count}"
