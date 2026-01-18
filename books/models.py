from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
import re
from django.urls import reverse
from cloudinary.models import CloudinaryField
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.postgres.indexes import GinIndex

def book_folder(instance):
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
            models.Index(fields=["name"]),
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
            ),
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
    book_language = models.CharField(max_length=100, blank=True, null=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_books"
    )

    # Cloudinary fields
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
        resource_type="video",
        folder=book_folder,
        blank=True,
        null=True
    )


    is_draft = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.PositiveIntegerField(default=0, db_index=True)
    read_later_count = models.PositiveIntegerField(default=0, db_index=True)
    views_count = models.PositiveIntegerField(default=0, db_index=True)

    objects = BookQuerySet.as_manager()

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["title"]),
            models.Index(fields=["-uploaded_at"]),
            GinIndex(
                name='book_trgm_idx',
                fields=['title', 'author', 'slug'],
                opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops'],
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = f"{slugify(self.slug)}-by-{slugify(self.author)}"
            unique_slug = base_slug
            counter = 1
            while Book.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('book', args=[self.slug])



# BOOK CONTENT MODEL


class BookContent(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name="content")
    content = CKEditor5Field("content", config_name="extends")
    chunks = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.content:
            pattern = r'(</p>|</div>|<br\s*/?>)'
            parts = re.split(pattern, self.content, flags=re.IGNORECASE)

            clean_chunks = []
            current_buffer = ""

            for part in parts:
                current_buffer += part
                # If this part was a closing tag/break, finalize the chunk
                if re.match(pattern, part, re.IGNORECASE):
                    # Only add if it has actual content (ignore empty paragraphs)
                    if re.search(r'[a-zA-Z0-9]', current_buffer): 
                        clean_chunks.append(current_buffer)
                    current_buffer = "" # Reset buffer

            # Append any remaining text
            if current_buffer.strip():
                clean_chunks.append(current_buffer)

            # Fallback: If split failed (chunk len is 1), force split by character count
            if len(clean_chunks) < 2 and len(self.content) > 1000:
                # Naive split every 1000 chars if HTML structure is broken
                clean_chunks = [self.content[i:i+1000] for i in range(0, len(self.content), 1000)]

            self.chunks = clean_chunks
        else:
            self.chunks = []
            
        super().save(*args, **kwargs)

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
            ),  
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
        ]

    def __str__(self):
        return f"{self.user.username} readed {self.book.title} "
    


class SearchQueryLog(models.Model):
    query = models.CharField(max_length=255, unique=True, db_index=True)
    count = models.PositiveIntegerField(default=1)
    first_searched = models.DateTimeField(auto_now_add=True)
    last_searched = models.DateTimeField(auto_now=True) 

    class Meta:
        ordering = ['-last_searched']
        verbose_name = "Failed Search Term"
        verbose_name_plural = "Failed Search Terms"

    def __str__(self):
        return f"{self.query} ({self.count} times)"
    
    
