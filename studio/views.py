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
from .models import ServiceType, Portfolio, Service, Booking, Profile
from .forms import RegisterForm, BookingForm
import logging
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q
from django.views.decorators.http import require_POST  # Добавьте этот импорт

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




# Добавляем новые импорты в начало файла
from .forms import (
    RecordingServiceForm, MixingServiceForm, 
    InstrumentalServiceForm, LyricsServiceForm,
    FullSongServiceForm, CreateServiceForm
)
from .models import (
    RecordingServiceParams, MixingServiceParams,
    InstrumentalServiceParams, LyricsServiceParams,
    FullSongServiceParams
)

# Обновляем service_detail view
@login_required
def service_detail(request, pk):
    service_type = get_object_or_404(ServiceType, pk=pk)
    
    form_mapping = {
        'recording': RecordingServiceForm,
        'mixing': MixingServiceForm,
        'instrumental': InstrumentalServiceForm,
        'lyrics': LyricsServiceForm,
        'full_song': FullSongServiceForm,
    }
    
    params_form_class = form_mapping.get(service_type.category)
    
    if request.method == 'POST':
        params_form = params_form_class(request.POST, request.FILES)
        
        if params_form.is_valid():
            try:
                # Создаем услугу
                service = Service(
                    client=request.user,
                    service_type=service_type,
                    status='pending',
                    price=service_type.min_price,
                    date_ordered=timezone.now()
                )
                
                # Рассчитываем цену
                cleaned_data = params_form.cleaned_data
                
                if service_type.category == 'recording':
                    if cleaned_data['hours'] >= 3 and not cleaned_data['unknown_hours']:
                        service.price += 500 * cleaned_data['hours']
                    if not cleaned_data['sound_engineer']:
                        service.price -= 200
                elif service_type.category == 'mixing':
                    if cleaned_data['express']:
                        service.price += 500
                    if cleaned_data['mastering']:
                        service.price += 300
                elif service_type.category == 'instrumental':
                    if cleaned_data['remake_beat']:
                        service.price += 1000
                
                service.save()
                
                # Создаем параметры
                params = params_form.save(commit=False)
                params.service = service
                params.save()
                
                messages.success(request, f"Заявка на {service_type.name} создана!")
                return redirect('profile')
                
            except Exception as e:
                logger.error(f"Service creation error: {str(e)}")
                messages.error(request, f"Ошибка: {str(e)}")
    else:
        params_form = params_form_class()
    
    context = {
        'service': service_type,
        'params_form': params_form,
        'now': timezone.now().strftime("%Y-%m-%d")
    }
    
    return render(request, f'studio/service_{service_type.category}.html', context)

# Удаляем старую BookingForm (если больше не используется)
# Или оставляем для других целей

# Обновляем profile view для отображения параметров услуг
@login_required
def profile(request):
    # Обработка загрузки аватара
    if request.method == 'POST' and 'avatar' in request.FILES:
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Аватар успешно обновлен!')
        return redirect('profile')
    
    # Получаем активные заказы (не завершенные и не отмененные)
    active_orders = Service.objects.filter(
        client=request.user
    ).exclude(
        Q(status='completed') | Q(status='canceled')
    ).order_by('-date_ordered')
    
    # Получаем завершенные заказы
    completed_orders = Service.objects.filter(
        client=request.user,
        status='completed'
    ).order_by('-date_completed')
    
    # Готовим данные для отображения
    active_orders_data = []
    for order in active_orders:
        params = None
        if hasattr(order, 'recording_params'):
            params = order.recording_params
        elif hasattr(order, 'mixing_params'):
            params = order.mixing_params
        elif hasattr(order, 'instrumental_params'):
            params = order.instrumental_params
        elif hasattr(order, 'lyrics_params'):
            params = order.lyrics_params
        elif hasattr(order, 'full_song_params'):
            params = order.full_song_params
        
        active_orders_data.append({
            'service': order,
            'params': params
        })
    
    completed_orders_data = []
    for order in completed_orders:
        params = None
        if hasattr(order, 'recording_params'):
            params = order.recording_params
        elif hasattr(order, 'mixing_params'):
            params = order.mixing_params
        elif hasattr(order, 'instrumental_params'):
            params = order.instrumental_params
        elif hasattr(order, 'lyrics_params'):
            params = order.lyrics_params
        elif hasattr(order, 'full_song_params'):
            params = order.full_song_params
        
        completed_orders_data.append({
            'service': order,
            'params': params
        })
    
    return render(request, 'studio/profile.html', {
        'user': request.user,
        'active_bookings': active_orders_data,
        'completed_orders': completed_orders_data
    })
@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Service, id=order_id, client=request.user)
    
    if order.status == 'pending':
        order.status = 'canceled'
        order.save()
        messages.success(request, 'Заказ успешно отменен')
        return JsonResponse({'status': 'success'})
    
    messages.error(request, 'Невозможно отменить заказ в текущем статусе')
    return JsonResponse({'status': 'error'}, status=400)

def home(request):
    # Порядок категорий для сортировки
    CATEGORY_ORDER = ['recording', 'mixing', 'instrumental', 'lyrics', 'full_song']
    
    services = sorted(
        ServiceType.objects.filter(is_active=True),
        key=lambda x: CATEGORY_ORDER.index(x.category)
    )[:5]
    
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