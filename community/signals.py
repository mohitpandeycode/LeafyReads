from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post, Comment

# 1. Main Cache Invalidator
# This handles New Posts, Deleted Posts, AND Like Updates 
@receiver([post_save, post_delete], sender=Post)
def invalidate_community_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern("community_feed:page:*")
    except AttributeError:
        cache.clear()

# 2. Update Like Count (Calculates count & Saves Post )
@receiver(m2m_changed, sender=Post.likes.through)
def update_post_likes_count(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.likes_count = instance.likes.count()
        instance.save(update_fields=['likes_count']) 

# 3. Comment Counts
@receiver(post_save, sender=Comment)
def update_comment_count_save(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.comments_count = post.comments.count()
        post.save(update_fields=['comments_count'])

@receiver(post_delete, sender=Comment)
def update_comment_count_delete(sender, instance, **kwargs):
    post = instance.post
    post.comments_count = post.comments.count()
    post.save(update_fields=['comments_count'])