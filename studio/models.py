# coding=windows-1251
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

class ServiceType(models.Model):
    SERVICE_CATEGORIES = [
        ('recording', 'Запись'),
        ('mixing', 'Сведение'),
        ('instrumental', 'Написание инструментала'),
        ('lyrics', 'Написание текста'),
        ('full_song', 'Песня под ключ'),
    ]
    
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES, default='recording')
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_price = models.IntegerField()
    duration = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    date_confirmed = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.IntegerField()
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.client.username} - {self.service_type.name}"

    def get_status_display(self):
        statuses = dict(self.STATUS_CHOICES)
        return statuses.get(self.status, self.status)

# Модели для параметров услуг
class RecordingServiceParams(models.Model):
    RECORDING_TYPES = [
        ('instrument', 'Инструмент'),
        ('vocal', 'Вокал'),
    ]
    
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='recording_params')
    recording_type = models.CharField(max_length=20, choices=RECORDING_TYPES)
    hours = models.IntegerField()
    unknown_hours = models.BooleanField(default=False)
    sound_engineer = models.BooleanField()
    datetime = models.DateTimeField()

class MixingServiceParams(models.Model):
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='mixing_params')
    zip_file = models.FileField(upload_to='mixing_zips/')
    references = models.FileField(upload_to='mixing_refs/')
    express = models.BooleanField(default=False)
    mastering = models.BooleanField(default=True)
    deadline = models.DateTimeField()

class InstrumentalServiceParams(models.Model):
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='instrumental_params')
    references = models.FileField(upload_to='instrumental_refs/')
    remake_beat = models.BooleanField(default=False)
    deadline = models.DateTimeField()

class LyricsServiceParams(models.Model):
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='lyrics_params')
    references = models.FileField(upload_to='lyrics_refs/')
    deadline = models.DateTimeField()

class FullSongServiceParams(models.Model):
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='full_song_params')
    references = models.FileField(upload_to='full_song_refs/')
    deadline = models.DateTimeField()

# Оригинальные модели (оставлены без изменений)
class Portfolio(models.Model):
    title = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='portfolio/')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Booking(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    date = models.DateTimeField()
    notes = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.username} - {self.service_type.name} ({self.date})"

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.author.username}"