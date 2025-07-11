from django.shortcuts import render

from books.models import Book, BookContent

def home(request):
    books = Book.objects.all()
    return render(request, 'home.html', {
        'books': books
    })
