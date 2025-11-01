from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from books.models import Book, BookContent
from .models import BookLog


@receiver(post_save, sender=Book)
def log_book_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    BookLog.objects.create(
        user=getattr(instance, "_updated_by", None),
        book=instance,
        action=action,
        message=f"Book '{instance.title}' was {'created' if created else 'updated'}."
    )


@receiver(pre_delete, sender=Book)
def log_book_delete(sender, instance, **kwargs):
    BookLog.objects.create(
        user=getattr(instance, "_updated_by", None),
        book=instance,
        action="delete",
        message=f"Book '{instance.title}' was deleted."
    )


@receiver(post_save, sender=BookContent)
def log_content_update(sender, instance, created, **kwargs):
    BookLog.objects.create(
        user=getattr(instance.book, "_updated_by", None),
        book=instance.book,
        action="content_update",
        message=f"Book content for '{instance.book.title}' was {'created' if created else 'updated'}."
    )
