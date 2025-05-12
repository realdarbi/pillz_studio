from django.contrib import admin

from .models import Profile, ServiceType, Service, Portfolio, Booking, Review

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')

admin.site.register(ServiceType)
admin.site.register(Service)
admin.site.register(Portfolio)
admin.site.register(Booking)
admin.site.register(Review)
