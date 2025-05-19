from django.contrib import admin
from .models import (
    Profile, ServiceType, Service, 
    Portfolio, Booking, Review,
    RecordingServiceParams, MixingServiceParams,
    InstrumentalServiceParams, LyricsServiceParams,
    FullSongServiceParams
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'bio_short')
    search_fields = ('user__username', 'phone')
    
    def bio_short(self, obj):
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
    bio_short.short_description = 'Bio'

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'min_price', 'duration', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'service_type', 'status', 'price', 'date_ordered')
    list_filter = ('status', 'service_type')
    search_fields = ('client__username', 'service_type__name')
    date_hierarchy = 'date_ordered'

@admin.register(RecordingServiceParams)
class RecordingServiceParamsAdmin(admin.ModelAdmin):
    list_display = ('service', 'recording_type', 'hours', 'unknown_hours', 'sound_engineer', 'datetime')
    list_filter = ('recording_type', 'unknown_hours', 'sound_engineer')
    search_fields = ('service__client__username',)
    date_hierarchy = 'datetime'

@admin.register(MixingServiceParams)
class MixingServiceParamsAdmin(admin.ModelAdmin):
    list_display = ('service', 'express', 'mastering', 'deadline')
    list_filter = ('express', 'mastering')
    date_hierarchy = 'deadline'

@admin.register(InstrumentalServiceParams)
class InstrumentalServiceParamsAdmin(admin.ModelAdmin):
    list_display = ('service', 'remake_beat', 'deadline')
    list_filter = ('remake_beat',)
    date_hierarchy = 'deadline'

@admin.register(LyricsServiceParams)
class LyricsServiceParamsAdmin(admin.ModelAdmin):
    list_display = ('service', 'deadline')
    date_hierarchy = 'deadline'

@admin.register(FullSongServiceParams)
class FullSongServiceParamsAdmin(admin.ModelAdmin):
    list_display = ('service', 'deadline')
    date_hierarchy = 'deadline'

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'service_type', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'service_type', 'date', 'is_confirmed')
    list_filter = ('is_confirmed', 'service_type')
    search_fields = ('client__username', 'notes')
    date_hierarchy = 'date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'service', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('author__username', 'text')
    date_hierarchy = 'created_at'