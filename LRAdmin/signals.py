from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone  # <--- Import this
from datetime import timedelta     # <--- Import this
from books.models import Book, BookContent
from .models import BookLog

# Helper function to delete old logs
def cleanup_old_logs():
    thirty_days_ago = timezone.now() - timedelta(days=30)
    # This deletes all logs older than 30 days in one fast query
    BookLog.objects.filter(timestamp__lt=thirty_days_ago).delete()

@receiver(post_save, sender=Book)
def log_book_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    BookLog.objects.create(
        user=getattr(instance, "_updated_by", None),
        book=instance,
        action=action,
        message=f"Book '{instance.title}' was {'created' if created else 'updated'}."
    )
    cleanup_old_logs()

@receiver(pre_delete, sender=Book)
def log_book_delete(sender, instance, **kwargs):
    BookLog.objects.create(
        user=getattr(instance, "_updated_by", None),
        book=instance,
        action="delete",
        message=f"Book '{instance.title}' was deleted."
    )
    cleanup_old_logs()

@receiver(post_save, sender=BookContent)
def log_content_update(sender, instance, created, **kwargs):
    user = getattr(instance, "_updated_by", None) 
    if not user:
        user = getattr(instance.book, "_updated_by", None)

    BookLog.objects.create(
        user=user,
        book=instance.book,
        action="content_update",
        message=f"Book content for '{instance.book.title}' was {'created' if created else 'updated'}."
    )
