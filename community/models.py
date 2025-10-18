from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from books.models import Book
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Helper function to define a clean upload path for post images
def post_image_upload_path(instance, filename):

    return f'post_images/user_{instance.post.author.id}/post_{instance.post.id}/{filename}'

# Create your models here.

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='community_posts')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_posts', blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['book']),
        ]

    def __str__(self):
        if self.book:
            return f'Post by {self.author.username} about "{self.book.title}"'
        return f'Post by {self.author.username} at {self.created_at.strftime("%Y-%m-%d %H:%M")}'
    
    def number_of_likes(self):
        return self.likes.count()
    
    def number_of_comments(self):
        return self.comments.count()

# NEW MODEL to handle multiple images per post
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=post_image_upload_path)

    def __str__(self):
        return f'Image for post {self.post.id}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_comments', blank=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['author']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        if self.parent:
            return f'Reply by {self.author.username} on comment {self.parent.id}'
        return f'Comment by {self.author.username} on post {self.post.id}'

    def number_of_likes(self):
        return self.likes.count()
        
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    verb = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['recipient']),
        ]

    def __str__(self):
        return f'Notification for {self.recipient.username}: {self.sender.username} {self.verb}'