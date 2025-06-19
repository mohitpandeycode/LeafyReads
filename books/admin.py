from django.contrib import admin

# Register your models here.
from django.contrib import admin
from books.models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

class BookPageInline(admin.TabularInline):
    model = BookPage
    extra = 0

class BookContentInline(admin.StackedInline):
    model = BookContent
    extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'category', 'price', 'is_published', 'uploaded_at')
    list_filter = ('genre', 'category', 'is_published')
    search_fields = ('title', 'author', 'isbn')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BookContentInline, BookPageInline]

@admin.register(BookContent)
class BookContentAdmin(admin.ModelAdmin):
    list_display = ('book', 'updated_at')
    search_fields = ('book__title',)

@admin.register(BookPage)
class BookPageAdmin(admin.ModelAdmin):
    list_display = ('book', 'page_number')
    list_filter = ('book',)
    search_fields = ('book__title', 'content')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'created_at')
    search_fields = ('user__username', 'book__title')
    list_filter = ('rating',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    search_fields = ('user__username', 'book__title')

@admin.register(ReadLater)
class ReadLaterAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'saved_at')
    search_fields = ('user__username', 'book__title')
