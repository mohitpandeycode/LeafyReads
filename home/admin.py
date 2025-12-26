from django.contrib import admin
from unfold.admin import ModelAdmin
from home.models import Notification

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('recipient', 'actor','notification_type')
    notification_type = ('book__title',)