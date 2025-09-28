from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.postgres.indexes import GinIndex  # For PostgreSQL full-text search

# Custom upload path for images and PDFs
def book_media_upload_path(instance, filename):
    folder = slugify(instance.title)
    return os.path.join('books', folder, filename)



# CATEGORY MODEL

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),  # Added index for faster filtering by name
        ]

    def __str__(self):
        return self.name



# GENRE MODEL

class Genre(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='genres')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    lucidicon = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['name']
        unique_together = ('category', 'name')
        indexes = [
            models.Index(fields=['category', 'slug']),  # Added index for category+slug lookups
        ]

    def __str__(self):
        return self.name



# BOOK MODEL

class Book(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=100)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='books')
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    cover_front = models.ImageField(upload_to=book_media_upload_path)
    pdf_file = models.FileField(upload_to=book_media_upload_path, blank=True, null=True)
    is_published = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    audio_file = models.FileField(upload_to='sounds/', null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['slug']),           # Existing index
            models.Index(fields=['title']),          # Existing index
            models.Index(fields=['genre']),          # Added index for genre filtering
            models.Index(fields=['-uploaded_at']),   # Added index for ordering by uploaded_at
            GinIndex(fields=['title', 'author']),    # Added for PostgreSQL full-text search
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



# BOOK CONTENT MODEL

class BookContent(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='content')
    content = CKEditor5Field('content', config_name='extends')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Content for {self.book.title}"



# REVIEW MODEL

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'book')
        indexes = [
            models.Index(fields=['book', 'user']),       # Added index for queries by book/user
            models.Index(fields=['-created_at']),        # Added index for ordering reviews quickly
        ]

    def __str__(self):
        return f"Review by {self.user.username} on {self.book.title}"



# LIKE MODEL

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        indexes = [
            models.Index(fields=['user', 'book']),   # Existing composite index
            models.Index(fields=['book']),           # Added index for queries by book
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.book.title}"



# READ LATER MODEL

class ReadLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        indexes = [
            models.Index(fields=['user', 'book']),   # Existing composite index
            models.Index(fields=['book']),           # Added index for queries by book
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.book.title} for later"
