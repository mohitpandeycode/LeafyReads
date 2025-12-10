from django.db import models
from books.models import Book
from django.contrib.auth.models import User


class BookLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Deleted"),
        ("content_update", "Content Updated"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="book_logs")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        book_title = self.book.title if self.book else "Deleted Book"
        user_name = self.user.username if self.user else "System"
        return f"{book_title} - {self.get_action_display()} by {user_name}"
