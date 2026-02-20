from django.contrib import admin
from unfold.admin import ModelAdmin
from home.models import Notification,Feedback

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('recipient', 'actor','notification_type')
    list_filter = ('notification_type',)
    
@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    list_display = ('user', 'feedback_type','message')
    list_filter = ('feedback_type',)