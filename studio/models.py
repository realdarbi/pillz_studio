# coding=windows-1251

from django.db import models
from django.contrib.auth.models import User

# Дополнительные поля для пользователя (аватар, никнейм и т.д.)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь с User
    avatar = models.ImageField(upload_to='avatars/', blank=True)  # Аватар
    phone = models.CharField(max_length=20, blank=True)  # Телефон
    bio = models.TextField(blank=True)  # О себе

class ServiceType(models.Model):
    name = models.CharField(max_length=100)  # Название (например, "Сведение")
    description = models.TextField()  # Описание услуги
    min_price = models.IntegerField()  # Минимальная цена
    duration = models.CharField(max_length=50)  # Пример: "2 часа", "3 дня"
    is_active = models.BooleanField(default=True)  # Доступна ли услуга !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def __str__(self):
        return self.name


class Service(models.Model):
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # Тип услуги
    client = models.ForeignKey(User, on_delete=models.CASCADE)  # Кто заказал
    date_ordered = models.DateTimeField(auto_now_add=True)  # Дата заказа
    date_completed = models.DateTimeField(null=True, blank=True)  # Дата выполнения
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'В обработке'),
            ('in_progress', 'В работе'),
            ('completed', 'Завершено'),
        ],
        default='pending'
    )
    price = models.IntegerField()  # Финальная цена (может отличаться от min_price)

    def __str__(self):
        return f"{self.client.username} - {self.service_type.name}"

class Portfolio(models.Model):
    title = models.CharField(max_length=100)  # Название трека/проекта
    audio_file = models.FileField(upload_to='portfolio/')  # Файл (mp3, wav)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # К какой услуге относится
    description = models.TextField(blank=True)  # Описание
    created_at = models.DateTimeField(auto_now_add=True)  # Дата добавления

    def __str__(self):
        return self.title

class Booking(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)  # Клиент
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # Услуга
    date = models.DateTimeField()  # Дата и время записи
    notes = models.TextField(blank=True)  # Пожелания клиента
    is_confirmed = models.BooleanField(default=False)  # Подтверждено ли

    def __str__(self):
        return f"{self.client.username} - {self.service_type.name} ({self.date})"

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Автор
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Услуга
    text = models.TextField()  # Текст отзыва
    rating = models.IntegerField(
        choices=[
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ],
        default=5)  # Оценка
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.author.username}"