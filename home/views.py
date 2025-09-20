from django.shortcuts import render

from books.models import *

def home(request):
    category = Genre.objects.all()
    books = Book.objects.select_related('genre')[:12]
    return render(request, 'home.html', {
        'books': books,
        'category': category
    })



    