# coding=windows-1251

from django.db import models
from django.contrib.auth.models import User

# �������������� ���� ��� ������������ (������, ������� � �.�.)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ����� � User
    avatar = models.ImageField(upload_to='avatars/', blank=True)  # ������
    phone = models.CharField(max_length=20, blank=True)  # �������
    bio = models.TextField(blank=True)  # � ����

class ServiceType(models.Model):
    name = models.CharField(max_length=100)  # �������� (��������, "��������")
    description = models.TextField()  # �������� ������
    min_price = models.IntegerField()  # ����������� ����
    duration = models.CharField(max_length=50)  # ������: "2 ����", "3 ���"
    is_active = models.BooleanField(default=True)  # �������� �� ������ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def __str__(self):
        return self.name


class Service(models.Model):
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # ��� ������
    client = models.ForeignKey(User, on_delete=models.CASCADE)  # ��� �������
    date_ordered = models.DateTimeField(auto_now_add=True)  # ���� ������
    date_completed = models.DateTimeField(null=True, blank=True)  # ���� ����������
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '� ���������'),
            ('in_progress', '� ������'),
            ('completed', '���������'),
        ],
        default='pending'
    )
    price = models.IntegerField()  # ��������� ���� (����� ���������� �� min_price)

    def __str__(self):
        return f"{self.client.username} - {self.service_type.name}"

class Portfolio(models.Model):
    title = models.CharField(max_length=100)  # �������� �����/�������
    audio_file = models.FileField(upload_to='portfolio/')  # ���� (mp3, wav)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # � ����� ������ ���������
    description = models.TextField(blank=True)  # ��������
    created_at = models.DateTimeField(auto_now_add=True)  # ���� ����������

    def __str__(self):
        return self.title

class Booking(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)  # ������
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)  # ������
    date = models.DateTimeField()  # ���� � ����� ������
    notes = models.TextField(blank=True)  # ��������� �������
    is_confirmed = models.BooleanField(default=False)  # ������������ ��

    def __str__(self):
        return f"{self.client.username} - {self.service_type.name} ({self.date})"

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # �����
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # ������
    text = models.TextField()  # ����� ������
    rating = models.IntegerField(
        choices=[
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ],
        default=5)  # ������
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"����� �� {self.author.username}"