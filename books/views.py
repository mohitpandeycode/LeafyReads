from django.shortcuts import render, get_object_or_404
from books.models import Book, BookContent

def home(request):
    book_content = BookContent.objects.first()
    book = Book.objects.first()

    if not book_content or not book:
        return render(request, 'not_found.html', status=404)  # Or show a proper message/template

    return render(request, 'book.html', {
        'bookcontent': book_content.content,
        'book': book
    })
