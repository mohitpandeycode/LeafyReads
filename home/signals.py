from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models.signals import post_save, m2m_changed,post_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from community.models import Post, Comment
from home.models import Notification
from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading
import logging

@receiver(user_logged_in)
def show_login_message(sender, request, user, **kwargs):
    messages.success(request, f"Welcome back, {user.first_name or user.username}!")



# SIGNAL: User likes a Post
@receiver(m2m_changed, sender=Post.likes.through)
def notify_post_like(sender, instance, action, pk_set, **kwargs):
    # We only trigger this when a like is ADDED (not removed)
    if action == 'post_add':
        # pk_set contains the ID(s) of the user(s) who just liked the post
        for user_id in pk_set:
            liker = User.objects.get(pk=user_id)
            
            # 1. Don't notify if I like my own post
            if liker != instance.author:
                
                # 2. Get a preview of the post title or content
                # If the post is about a book, use the book title. Otherwise, use content.
                post_preview = "Update"
                if instance.book:
                    post_preview = instance.book.title
                elif instance.content:
                    # Slice first 20 chars if it's just text
                    post_preview = instance.content[:40] + "..." if len(instance.content) > 40 else instance.content

                # 3. Create the HTML message
                msg = f"<strong>{liker.username}</strong> liked your post <strong>“{post_preview}”</strong> ❤️"

                # 4. Create the Notification
                Notification.objects.create(
                    recipient=instance.author,
                    actor=liker,
                    notification_type='like',
                    content_object=instance, # Links to the Post so clicking it goes to the post
                    message=msg
                )
                
# 1. NOTIFY: New Comment
@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, created, **kwargs):
    if created:
        post_author = instance.post.author
        commenter = instance.author

        if post_author != commenter:
            # We construct the HTML string here
            # Truncate post content if it doesn't have a title (posts usually just have content)
            post_preview = instance.post.content[:40] + "..." 
            if hasattr(instance.post, 'title') and instance.post.title:
                post_preview = instance.post.title
            
            msg = f"<strong>{commenter.username}</strong> commented on your post <strong>“{post_preview}”</strong> 💬"

            Notification.objects.create(
                recipient=post_author,
                actor=commenter,
                notification_type='comment',
                content_object=instance.post,
                message=msg
            )

# 2. NOTIFY: Book Mention in Post
@receiver(post_save, sender=Post)
def notify_book_mention(sender, instance, created, **kwargs):
    if created and instance.book:
        if instance.book.uploaded_by:
            book_uploader = instance.book.uploaded_by
            post_author = instance.author

            if book_uploader != post_author:
                msg = f"<strong>{post_author.username}</strong> mentioned your book <strong>“{instance.book.title}”</strong> in a discussion 📚"

                Notification.objects.create(
                    recipient=book_uploader,
                    actor=post_author,
                    notification_type='book_mention',
                    content_object=instance,
                    message=msg
                )

# 3. NOTIFY: Post Published (Self-Notification)
@receiver(post_save, sender=Post)
def notify_post_publish(sender, instance, created, **kwargs):
    if created:
        # Create a title preview from content if title doesn't exist
        post_preview = instance.content[:30] + "..."
        
        msg = f"<strong>Your post “{post_preview}”</strong> has been published to the community 📢"

        Notification.objects.create(
            recipient=instance.author,
            actor=instance.author,
            notification_type='post_publish',
            content_object=instance,
            message=msg
        )
        
# 4. CLEANUP: When a Post is Deleted
@receiver(post_delete, sender=Post)
def cleanup_post_notifications(sender, instance, **kwargs):
    # 1. Get the ContentType for the Post model
    post_content_type = ContentType.objects.get_for_model(Post)
    
    # 2. Find and delete all notifications linked to this specific post
    # This removes "User liked your post", "User commented...", etc.
    Notification.objects.filter(
        content_type=post_content_type, 
        object_id=instance.id
    ).delete()
    
    
# 5. NOTIFY: Post Deleted
@receiver(post_delete, sender=Post)
def notify_post_delete(sender, instance, **kwargs):
    # 1. Prepare the data we need
    author_id = instance.author.id
    
    post_preview = "Update"
    if instance.book:
        post_preview = instance.book.title
    elif instance.content:
        post_preview = instance.content[:30] + "..." if len(instance.content) > 30 else instance.content

    msg = f"<strong>Your post “{post_preview}”</strong> has been deleted. 🗑️"

    # 2. Define the creation task
    def create_notification_safely():
        try:
            # We fetch the user Freshly. 
            # If the user was deleted in the transaction, this query or the create will fail.
            author = User.objects.get(pk=author_id)
            
            Notification.objects.create(
                recipient=author,
                actor=author,
                notification_type='post_delete',
                content_object=author,
                message=msg
            )
        except (User.DoesNotExist, IntegrityError):
            pass

    # 3. Schedule it to run AFTER the transaction commits
    transaction.on_commit(create_notification_safely)
    
# Send email when new user login
    
logger = logging.getLogger(__name__)

# --- 1. The Background Task (Worker) ---
def send_welcome_email_thread(user_email, first_name):
    try:
        subject = "Welcome to LeafyReads"
        context = {
            'user': {'first_name': first_name},
        }
        
        # Render the HTML
        html_message = render_to_string('emails/welcome_email.html', context)
        
        # Plain text fallback
        plain_message = f"Welcome to LeafyReads, {first_name}! Thank you for creating an account. Please explore our library and track your reading progress."
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user_email}")
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")

# --- 2. The Trigger (Listener) ---
@receiver(user_signed_up)
def trigger_welcome_email(request, user, **kwargs):
    """
    Listens for any new user signup and triggers the email thread.
    """
    if user.email:
        # Get name or default to 'Reader'
        first_name = user.first_name if user.first_name else "Reader"
        
        # Start the background thread
        email_thread = threading.Thread(
            target=send_welcome_email_thread,
            args=(user.email, first_name)
        )
        email_thread.start()