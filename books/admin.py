
# Register your models here.
from django.contrib import admin
from unfold.admin import ModelAdmin
from books.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ('name',)

class BookContentInline(admin.StackedInline):
    model = BookContent
    extra = 0

@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ('title', 'author', 'genre', 'price', 'is_published', 'uploaded_at')
    list_filter = ('genre', 'is_published')
    search_fields = ('title', 'author', 'isbn')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BookContentInline] 

@admin.register(BookContent)
class BookContentAdmin(ModelAdmin):
    list_display = ('book', 'updated_at')
    search_fields = ('book__title',)

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('user', 'book', 'rating', 'created_at')
    search_fields = ('user__username', 'book__title')
    list_filter = ('rating',)

@admin.register(Like)
class LikeAdmin(ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    search_fields = ('user__username', 'book__title')

@admin.register(ReadLater)
class ReadLaterAdmin(ModelAdmin):
    list_display = ('user', 'book', 'saved_at')
    search_fields = ('user__username', 'book__title')
    
@admin.register(ReadBy)
class ReadByAdmin(ModelAdmin):
    list_display = ('user', 'book', 'readed_at')
    search_fields = ('user__username', 'book__title')
