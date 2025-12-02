from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post

@receiver([post_save, post_delete], sender=Post)
def invalidate_community_cache(sender, instance, **kwargs):
    cache.delete("community_posts_list")