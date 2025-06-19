from django.shortcuts import render, get_object_or_404
from books.models import Book

def home(request):
    book = Book.objects.first()

    if book and hasattr(book, 'pages'):
        pages = book.pages.all()  # Already ordered by Meta
    else:
        pages = []

    return render(request, 'book.html', {'book': book, 'pages': pages})
