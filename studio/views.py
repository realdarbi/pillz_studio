# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_http_methods
from .models import ServiceType, Portfolio, Service, Booking
from .forms import RegisterForm, BookingForm
import logging
from django.utils.http import url_has_allowed_host_and_scheme

logger = logging.getLogger(__name__)

def is_ajax(request):
    
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

class CustomLoginView(LoginView):
    template_name = 'studio/login.html'
    
    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            try:
                context = self.get_context_data()
                context['is_ajax'] = True
                html = render_to_string(
                    'studio/login_form.html', 
                    context, 
                    request=request,
                    using='django'
                )
                return JsonResponse(
                    {'html': html},
                    content_type='application/json; charset=utf-8'
                )
            except Exception as e:
                logger.error(f"Error rendering login form: {str(e)}")
                return JsonResponse(
                    {'error': str(e)},
                    status=500,
                    content_type='application/json; charset=utf-8'
                )
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Обработка успешной авторизации"""
        if is_ajax(self.request):
            login(self.request, form.get_user())
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url(),  # Используем встроенный метод
                'user_authenticated': True  # Добавляем флаг аутентификации
            }, content_type='application/json; charset=utf-8')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Обработка неудачной авторизации"""
        if is_ajax(self.request):
            try:
                html = render_to_string(
                    'studio/login_form.html', 
                    {'form': form, 'is_ajax': True}, 
                    request=self.request,
                    using='django'
                )
                return JsonResponse({
                    'success': False,
                    'html': html,
                    'errors': form.errors.get_json_data()  # Добавляем ошибки формы
                }, status=400, content_type='application/json; charset=utf-8')
            except Exception as e:
                logger.error(f"Error rendering invalid login form: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Ошибка формы'
                }, status=500, content_type='application/json; charset=utf-8')
        return super().form_invalid(form)
    
    def get_success_url(self):
        """Определяем URL для перенаправления после успешного входа"""
        redirect_to = self.request.POST.get('next') or self.request.GET.get('next')
        if redirect_to and url_has_allowed_host_and_scheme(redirect_to, allowed_hosts=None):
            return redirect_to
        return super().get_success_url()
@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                
                if is_ajax(request):
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('home')
                    })
                return redirect('home')
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                if is_ajax(request):
                    return JsonResponse({
                        'success': False,
                        'html': render_to_string(
                            'studio/register_form.html',
                            {'form': form},
                            request=request
                        )
                    }, status=400)
                messages.error(request, f"Ошибка регистрации: {str(e)}")
        
        # Для AJAX возвращаем форму с ошибками
        if is_ajax(request):
            return JsonResponse({
                'success': False,
                'html': render_to_string(
                    'studio/register_form.html',
                    {'form': form},
                    request=request
                )
            }, status=400)
    
    # GET запрос
    form = RegisterForm()
    
    if is_ajax(request):
        return JsonResponse({
            'html': render_to_string(
                'studio/register_form.html',
                {'form': form},
                request=request
            )
        })
    
    return render(request, 'studio/register.html', {'form': form})
def custom_logout(request):
    
    logout(request)
    messages.success(request, "Вы успешно вышли из системы")
    return redirect(reverse('login'))

@login_required
def profile(request):
   
    user_bookings = Booking.objects.filter(client=request.user).order_by('-date')
    user_services = Service.objects.filter(client=request.user).order_by('-date_ordered')
    
    return render(request, 'studio/profile.html', {
        'user': request.user,
        'services': user_services,
        'bookings': user_bookings
    })

@login_required
def service_detail(request, pk):
    
    service = get_object_or_404(ServiceType, pk=pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.service_type = service
            booking.status = 'pending'
            
            if booking.date < timezone.now():
                messages.error(request, "Нельзя записаться на прошедшую дату")
            else:
                try:
                    booking.save()
                    messages.success(request, f"Вы успешно записались на {service.name}!")
                    return redirect('profile')
                except Exception as e:
                    messages.error(request, f"Ошибка при записи: {str(e)}")
    else:
        form = BookingForm(initial={
            'service_type': service,
            'date': timezone.now() + timezone.timedelta(days=1)
        })
    
    return render(request, 'studio/service_detail.html', {
        'service': service,
        'form': form,
        'now': timezone.now().strftime("%Y-%m-%d")
    })

def home(request):
    
    services = ServiceType.objects.filter(is_active=True)[:5]
    return render(request, 'studio/home.html', {
        'services': services,
        'title': 'Главная',
        'heading': 'Популярные услуги'
    })

def services_list(request):
    
    services = ServiceType.objects.filter(is_active=True)
    return render(request, 'studio/home.html', {
        'services': services,
        'title': 'Все услуги',
        'heading': 'Полный список услуг'
    })