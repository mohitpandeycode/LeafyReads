from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib import messages
from books.models import *

def home(request):
    category = Genre.objects.values('id', 'name','slug','lucidicon').order_by('pk')
    books = Book.objects.select_related('genre').only('id','title','genre_id')[:12]
    

    return render(request, 'home.html', {
        'books': books,
        'category': category
    })

def customLogout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home') 



    