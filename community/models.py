from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from books.models import Book
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
import uuid


def post_folder(instance):
    post = instance.post
    folder_name = slugify(post.book.title) if post.book else f"post-{post.id}"
    return f"community/{folder_name}"


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
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.book:
            return f'Post by {self.author.username} about "{self.book.title}"'
        return f'Post by {self.author.username} at {self.created_at.strftime("%Y-%m-%d %H:%M")}'
    
    def number_of_likes(self):
        return self.likes.count()
    
    def number_of_comments(self):
        return self.comments.count()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_content = self.content[:50] if self.content else "post"
            slug_candidate = slugify(base_content)
            short_uuid = str(uuid.uuid4())[:10]
            self.slug = f"{slug_candidate}-{short_uuid}"
        super().save(*args, **kwargs)

# NEW MODEL to handle multiple images per post
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField(
        "image",
        resource_type="image",
        folder=post_folder,
        transformation=[
        {
            "width": 1200,
            "height": 1200,
            "crop": "limit",   
            "quality": "auto:low",
            "fetch_format": "auto"
        }
    ]     
    )

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

    def __str__(self):
        if self.parent:
            return f'Reply by {self.author.username} on comment {self.parent.id}'
        return f'Comment by {self.author.username} on post {self.post.id}'

    def number_of_likes(self):
        return self.likes.count()
        