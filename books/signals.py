from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from books.models import Book, Genre, ReadBy, Like, ReadLater
from django.db.models import F

# --- 1. GENERAL CACHE INVALIDATION ---

@receiver([post_save, post_delete], sender=Book)
def invalidate_book_caches(sender, instance, **kwargs):
    # 1. Clear Home Cache
    cache.delete("home_books")
    try:
        cache.delete_pattern("library_books_*")
    except AttributeError:
        cache.delete("library_books_p1_snewest_l")

@receiver([post_save, post_delete], sender=Genre)
def invalidate_genre_caches(sender, instance, **kwargs):
    # Clears BOTH home categories and library categories
    cache.delete("home_categories")
    cache.delete("library_categories")

@receiver([post_save, post_delete], sender=ReadBy)
def invalidate_user_recent_books(sender, instance, **kwargs):
    user_id = instance.user.id
    cache.delete(f"library_recent_user_{user_id}")


@receiver(post_save, sender=Like)
def increment_likes(sender, instance, created, **kwargs):
    if created:
        Book.objects.filter(pk=instance.book.pk).update(likes_count=F('likes_count') + 1)

@receiver(post_delete, sender=Like)
def decrement_likes(sender, instance, **kwargs):
    Book.objects.filter(pk=instance.book_id, likes_count__gt=0).update(likes_count=F('likes_count') - 1)

@receiver(post_save, sender=ReadLater)
def increment_read_later(sender, instance, created, **kwargs):
    if created:
        Book.objects.filter(pk=instance.book.pk).update(read_later_count=F('read_later_count') + 1)

@receiver(post_delete, sender=ReadLater)
def decrement_read_later(sender, instance, **kwargs):
    Book.objects.filter(pk=instance.book_id, read_later_count__gt=0).update(read_later_count=F('read_later_count') - 1)