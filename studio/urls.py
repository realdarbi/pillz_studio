# -*- coding: utf-8 -*-

from django.urls import path, include  
from . import views
from django.contrib.auth.decorators import login_required
from .views import CustomLoginView

urlpatterns = [
    path('', views.home, name='home'),                     # Главная страница
    path('services/', views.services_list, name='services'),  # Все услуги
    path('service/<int:pk>/', views.service_detail, name='service_detail'),  # Конкретная услуга
    path('profile/', login_required(views.profile), name='profile'),       # Профиль пользователя
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),


    # Услуги
    path('service/<int:pk>/', views.service_detail, name='service_detail'),


]

