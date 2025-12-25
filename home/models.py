from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('comment', 'Comment'),
        ('book_mention', 'Book Mention'),
        ('post_publish', 'Post Published'),
        ('like', 'Like'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caused_notifications', null=True, blank=True)
    
    # We store the formatted HTML message here
    message = models.TextField() 
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Links to the actual object (Post, Book, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient}: {self.notification_type}"