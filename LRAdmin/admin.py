from django.contrib import admin
from LRAdmin.models import BookLog
from unfold.admin import ModelAdmin

@admin.register(BookLog)
class BookLogAdmin(ModelAdmin):
    list_display = ("book", "user", "action", "timestamp")
    list_filter = ("action", "timestamp", "user")
    search_fields = ("book__title", "message", "user__username")