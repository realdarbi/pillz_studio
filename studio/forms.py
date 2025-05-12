# coding=windows-1251
from django import forms
from .models import (
    Booking, User, 
    RecordingServiceParams, MixingServiceParams,
    InstrumentalServiceParams, LyricsServiceParams,
    FullSongServiceParams, Service
)
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateInput, DateTimeInput

# Общие формы (оставляем без изменений)
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service_type', 'date', 'notes']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Формы для услуг
class RecordingServiceForm(forms.ModelForm):
    datetime = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Дата и время записи"
    )
    
    class Meta:
        model = RecordingServiceParams
        fields = ['recording_type', 'hours', 'unknown_hours', 'sound_engineer', 'datetime']
        widgets = {
            'hours': forms.NumberInput(attrs={'min': 1, 'max': 7}),
        }

class MixingServiceForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Дедлайн"
    )
    
    class Meta:
        model = MixingServiceParams
        fields = ['zip_file', 'references', 'express', 'mastering', 'deadline']
        labels = {
            'zip_file': "ZIP-архив с треками",
            'references': "Референс-треки",
            'express': "Экспресс-сведение (700р)",
            'mastering': "Включить мастеринг (+500р)",
        }

class InstrumentalServiceForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Дедлайн"
    )
    
    class Meta:
        model = InstrumentalServiceParams
        fields = ['references', 'remake_beat', 'deadline']
        labels = {
            'remake_beat': "Нужен ремейк бита",
        }

# Аналогично для LyricsServiceForm и FullSongServiceForm
class LyricsServiceForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Дедлайн"
    )
    
    class Meta:
        model = LyricsServiceParams
        fields = ['references', 'deadline']

class FullSongServiceForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Дедлайн"
    )
    
    class Meta:
        model = FullSongServiceParams
        fields = ['references', 'deadline']

# Комбинированная форма для создания услуги
class CreateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }