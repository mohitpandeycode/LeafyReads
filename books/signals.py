from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from books.models import Book, Genre, ReadBy


@receiver([post_save, post_delete], sender=Book)
def invalidate_home_books(sender, instance, **kwargs):
    cache.delete("home_books")

@receiver([post_save, post_delete], sender=Genre)
def invalidate_home_categories(sender, instance, **kwargs):
    cache.delete("home_categories")
    
@receiver([post_save, post_delete], sender=Book)
def invalidate_library_books(sender, instance, **kwargs):
    cache.delete("home_books")
    try:
        cache.delete_pattern("library_books_page_*")
    except AttributeError:
        cache.delete("library_books_page_1")

@receiver([post_save, post_delete], sender=Genre)
def invalidate_library_categories(sender, instance, **kwargs):
    cache.delete("home_categories")
    cache.delete("library_categories")

@receiver([post_save, post_delete], sender=ReadBy)
def invalidate_user_recent_books(sender, instance, **kwargs):
    user_id = instance.user.id
    cache.delete(f"library_recent_user_{user_id}")