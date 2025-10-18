
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Post, PostImage, Comment, Notification

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1 

# --- Post Admin ---
@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('id', 'author', 'book', 'created_at', 'number_of_likes', 'number_of_comments')
    search_fields = ('content', 'author__username', 'book__title')
    list_filter = ('created_at', 'book')
    readonly_fields = ('created_at', 'updated_at', 'number_of_likes', 'number_of_comments')
    fieldsets = (
        (None, {
            'fields': ('author', 'book', 'content')
        }),
        ('Statistics', {
            'fields': ('number_of_likes', 'number_of_comments', 'created_at', 'updated_at')
        }),
        ('Relationships', {
            'fields': ('likes', 'mentioned_users')
        }),
    )

    inlines = [PostImageInline]
    
    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'
    
    def number_of_likes(self, obj):
        return obj.number_of_likes()
    number_of_likes.short_description = 'Likes'
    
    def number_of_comments(self, obj):
        return obj.number_of_comments()
    number_of_comments.short_description = 'Comments'


# --- Comment Admin ---
@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('id', 'author', 'post', 'parent', 'content_snippet', 'created_at', 'number_of_likes')
    search_fields = ('content', 'author__username', 'post__id')
    list_filter = ('created_at',)
    
    readonly_fields = ('created_at', 'updated_at', 'number_of_likes')
    
    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'
    
    def number_of_likes(self, obj):
        return obj.number_of_likes()
    number_of_likes.short_description = 'Likes'


# --- Notification Admin ---
@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('recipient', 'sender', 'verb', 'read', 'timestamp', 'target_info')
    search_fields = ('recipient__username', 'sender__username', 'verb')
    list_filter = ('read', 'verb', 'timestamp')
    
    readonly_fields = ('timestamp', 'content_type', 'object_id')

    # Custom method to display the target object
    def target_info(self, obj):
        if obj.target:
            return str(obj.target)
        return 'N/A'
    target_info.short_description = 'Target Object'