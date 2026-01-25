from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete,pre_save
from django.core.cache import cache
from books.models import Book, Genre, ReadBy, Like, ReadLater
from django.db.models import F
from home.models import Notification 
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import threading


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
    

@receiver(post_delete, sender=Book)
def delete_book_notifications(sender, instance, **kwargs):
    """
    When a Book is deleted, find and delete all notifications 
    linked to that specific book.
    """
    content_type = ContentType.objects.get_for_model(Book)
    
    Notification.objects.filter(
        content_type=content_type, 
        object_id=instance.id
    ).delete()



@receiver(pre_save, sender=Book)
def notify_user_on_publish(sender, instance, **kwargs):
    # Only run checks if the book already exists (it's an update, not a new create)
    if instance.pk: 
        try:
            # Fetch the OLD version of the book from the database
            old_book = Book.objects.get(pk=instance.pk)
            
            # CONDITION: Was unpublished, and is NOW published?
            if old_book.is_published is False and instance.is_published is True:
                
                # --- A. CREATE IN-APP NOTIFICATION ---
                try:
                    display_title = (instance.title[:30] + '..') if len(instance.title) > 30 else instance.title
                    
                    Notification.objects.create(
                        recipient=instance.uploaded_by,
                        notification_type='book_published', 
                        message=f'<strong>Congratulations!</strong> Your book <strong>{display_title}</strong> is now LIVE 🚀.',
                        content_type=ContentType.objects.get_for_model(Book),
                        object_id=instance.id
                    )
                except Exception as e:
                    print(f"Notification Creation Failed: {e}")

                # --- B. SEND EMAIL (With Safety Checks) ---
                user = instance.uploaded_by
                
                # Check 1: Does user have an email?
                if user.email:
                    try:
                        subject = f"Your book '{instance.title}' is now LIVE! 🚀"
                        
                        # Generate URL 
                        book_url = f"https://leafyreads.com/book/library/book-details/{instance.slug}/"
                        
                        # Check 2: Does book have a cover? (Avoid template crash)
                        cover_url = instance.cover_front.url if instance.cover_front else ""

                        # Render HTML Template
                        context = {
                            'user': user,
                            'book': instance,
                            'book_url': book_url,
                            'cover_url': cover_url 
                        }
                        
                        # Load 'templates/emails/book_published.html'
                        html_message = render_to_string('emails/book_published.html', context)
                        plain_message = strip_tags(html_message) # Fallback text
                        
                        # Start Thread
                        EmailThread(
                            subject=subject,
                            body=plain_message,
                            recipient_list=[user.email],
                            html_message=html_message
                        ).start()
                        
                    except Exception as e:
                        print(f"Email Generation Failed: {e}")

        except Book.DoesNotExist:
            # This happens only if the ID is somehow invalid 
            pass 
        except Exception as e:
            # Catch-all to ensure the Book Save is NEVER blocked
            print(f"General Signal Error: {e}")
        

# ==========================================
# 1. EMAIL THREADING CLASS (Prevents Server Freeze)
# ==========================================
class EmailThread(threading.Thread):
    def __init__(self, subject, body, recipient_list, html_message=None):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        """
        Sends email in a separate thread.
        Silences errors so the main app doesn't crash.
        """
        try:
            send_mail(
                self.subject,
                self.body,
                settings.DEFAULT_FROM_EMAIL,
                self.recipient_list,
                fail_silently=True, # Critical: If SMTP fails, code continues
                html_message=self.html_message
            )
        except Exception as e:
            # You can log this error to a file if you have logging set up
            print(f"Error sending email in thread: {e}")