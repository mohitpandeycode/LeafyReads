from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
from cloudinary.models import CloudinaryField
from django_ckeditor_5.fields import CKEditor5Field

def book_folder(instance):
    """Return a Cloudinary folder path for each book based on its title."""
    return f"books/{slugify(instance.title)}"



# Custom upload path for images and PDFs
def book_media_upload_path(instance, filename):
    folder = slugify(instance.title)
    return os.path.join("books", folder, filename)


# CATEGORY MODEL


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),  # Added index for faster filtering by name
        ]

    def __str__(self):
        return self.name


# GENRE MODEL


class Genre(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="genres"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    lucidicon = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("category", "name")
        indexes = [
            models.Index(
                fields=["category", "slug"]
            ),  # Added index for category+slug lookups
        ]

    def __str__(self):
        return self.name


class BookQuerySet(models.QuerySet):
    def with_related(self):
        return self.select_related("genre", "genre__category", "content")


# BOOK MODEL



class Book(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, max_length=255)
    author = models.CharField(max_length=100)
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, related_name="books"
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)

    # Cloudinary fields with per-book folders
    cover_front = CloudinaryField(
        "image",
        resource_type="image",
        folder=book_folder,
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
    pdf_file = CloudinaryField(
        "file",
        resource_type="raw",
        folder=book_folder,
        blank=True,
        null=True
    )
    audio_file = CloudinaryField(
        "audio",
        resource_type="video",  # Cloudinary treats audio as video
        folder=book_folder,
        blank=True,
        null=True
    )

    is_published = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BookQuerySet.as_manager()

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["title"]),
            models.Index(fields=["genre"]),
            models.Index(fields=["-uploaded_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = f"{slugify(self.title)}-by-{slugify(self.author)}"
            unique_slug = base_slug
            counter = 1
            while Book.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



# BOOK CONTENT MODEL


class BookContent(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name="content")
    content = CKEditor5Field("content", config_name="extends")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Content for {self.book.title}"


# REVIEW MODEL


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField()
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "book")
        indexes = [
            models.Index(
                fields=["book", "user"]
            ),  # Added index for queries by book/user
            models.Index(
                fields=["-created_at"]
            ),  # Added index for ordering reviews quickly
        ]

    def __str__(self):
        return f"Review by {self.user.username} on {self.book.title}"


# LIKE MODEL


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")
        indexes = [
            models.Index(fields=["user", "book"]),
            models.Index(fields=["book"]),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.book.title}"


# READ LATER MODEL


class ReadLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")
        indexes = [
            models.Index(fields=["user", "book"]),  # Existing composite index
            models.Index(fields=["book"]),  # Added index for queries by book
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.book.title} for later"


class ReadBy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="readby")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="readbooks")
    readed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")
        indexes = [
            models.Index(fields=["user", "book"]),
            models.Index(fields=["book"]),
        ]

    def __str__(self):
        return f"{self.user.username} readed {self.book.title} "
