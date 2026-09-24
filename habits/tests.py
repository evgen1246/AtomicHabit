from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit

User = get_user_model()


class HabitCRUDTestCase(APITestCase):
    """Тесты CRUD для привычек"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@test.ru", password="test12345")
        self.other_user = User.objects.create_user(
            email="other@test.ru", password="test12345"
        )

        self.client.force_authenticate(user=self.user)

        self.habit = Habit.objects.create(
            habit_creator=self.user,
            place="Дом",
            date_time="08:00:00",
            action="Выпить стакан воды",
            is_pleasant=False,
            periodicity=1,
            duration=60,
            is_public=False,
        )

    def test_create_habit(self):
        """Создание привычки"""
        url = reverse("habits:habit-list")
        data = {
            "place": "Офис",
            "date_time": "09:00:00",
            "action": "Сделать зарядку",
            "is_pleasant": False,
            "periodicity": 1,
            "duration": 60,
            "is_public": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)

    def test_list_own_habits(self):
        """Список своих привычек"""
        url = reverse("habits:habit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_habit(self):
        """Просмотр привычки"""
        url = reverse("habits:habit-detail", kwargs={"pk": self.habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "Выпить стакан воды")

    def test_update_own_habit(self):
        """Обновление своей привычки"""
        url = reverse("habits:habit-detail", kwargs={"pk": self.habit.pk})
        response = self.client.patch(url, {"action": "Новое действие"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, "Новое действие")

    def test_delete_own_habit(self):
        """Удаление своей привычки"""
        url = reverse("habits:habit-detail", kwargs={"pk": self.habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_cannot_update_foreign_habit(self):
        """Нельзя обновить чужую привычку"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("habits:habit-detail", kwargs={"pk": self.habit.pk})
        response = self.client.patch(url, {"action": "Взлом"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_foreign_habit(self):
        """Нельзя удалить чужую привычку"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("habits:habit-detail", kwargs={"pk": self.habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access_denied(self):
        """Неавторизованный не имеет доступа"""
        self.client.force_authenticate(user=None)
        url = reverse("habits:habit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_validation_duration_over_120(self):
        """Валидация: duration > 120"""
        url = reverse("habits:habit-list")
        data = {
            "place": "Дом",
            "date_time": "09:00:00",
            "action": "Тест",
            "periodicity": 1,
            "duration": 200,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_related_and_reward(self):
        """Валидация: related_habit + reward одновременно"""
        pleasant = Habit.objects.create(
            habit_creator=self.user,
            place="Дом",
            date_time="20:00:00",
            action="Ванна",
            is_pleasant=True,
            periodicity=1,
            duration=60,
        )
        url = reverse("habits:habit-list")
        data = {
            "place": "Дом",
            "date_time": "09:00:00",
            "action": "Тест",
            "periodicity": 1,
            "duration": 60,
            "related_habit": pleasant.id,
            "reward": "Конфета",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_periodicity_over_7(self):
        """Валидация: periodicity > 7"""
        url = reverse("habits:habit-list")
        data = {
            "place": "Дом",
            "date_time": "09:00:00",
            "action": "Тест",
            "periodicity": 14,
            "duration": 60,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_habits_visible_to_others(self):
        """Публичные привычки видны другим"""
        self.habit.is_public = True
        self.habit.save()

        self.client.force_authenticate(user=self.other_user)
        url = reverse("habits:habit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class UserTestCase(APITestCase):
    """Тесты для пользователей"""

    def test_register_user(self):
        """Регистрация пользователя"""
        url = reverse("users:register")
        data = {"email": "new@test.ru", "password": "newpass12345"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "new@test.ru")

    def test_login_user(self):
        """Вход пользователя по email"""
        User.objects.create_user(email="login@test.ru", password="test12345")
        url = reverse("users:token_obtain_pair")
        data = {"email": "login@test.ru", "password": "test12345"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        """Неверный пароль"""
        User.objects.create_user(email="wrong@test.ru", password="test12345")
        url = reverse("users:token_obtain_pair")
        data = {"email": "wrong@test.ru", "password": "wrong"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_telegram_link(self):
        """Привязка Telegram ID"""
        user = User.objects.create_user(email="tg@test.ru", password="test12345")
        self.client.force_authenticate(user=user)
        url = reverse("users:telegram_link")
        response = self.client.post(url, {"telegram_id": "123456789"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.telegram_id, "123456789")

    def test_telegram_link_without_id(self):
        """Привязка без telegram_id"""
        user = User.objects.create_user(email="tg2@test.ru", password="test12345")
        self.client.force_authenticate(user=user)
        url = reverse("users:telegram_link")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
