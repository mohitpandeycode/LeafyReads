from django.shortcuts import render

from books.models import *

def home(request):
    category = Genre.objects.all()
    books = Book.objects.all()
    return render(request, 'home.html', {
        'books': books,
        'category':category
    })

    