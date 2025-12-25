from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User
from community.models import Post, Comment
from home.models import Notification

@receiver(user_logged_in)
def show_login_message(sender, request, user, **kwargs):
    messages.success(request, f"Welcome back, {user.first_name or user.username}!")



# SIGNAL: User likes a Post
# Output: "JohnDoe liked your post “Top 5 Fantasy Books” ❤️"
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
# Output: "Priya Sharma commented on your post “Top 5 Fantasy Books” 💬"
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
# Output: "Daniel Lee mentioned your book “The Silent Forest” in a discussion 📚"
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
# Output: "Your post “Building a Reading Habit” has been published to the community 📢"
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