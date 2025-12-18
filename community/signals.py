from django.db.models.signals import post_save, post_delete,m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post

@receiver([post_save, post_delete], sender=Post)
def invalidate_community_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern("community_feed:page:*")
    except AttributeError:
        cache.clear()
        
# 2. Handle LIKES (The Many-to-Many Change)
@receiver(m2m_changed, sender=Post.likes.through)
def invalidate_likes(sender, instance, **kwargs):
    # Only clear cache when the add/remove is actually finished
    if kwargs.get('action') in ["post_add", "post_remove", "post_clear"]:
        try:
            cache.delete_pattern("community_feed:page:*")
        except AttributeError:
            cache.clear()