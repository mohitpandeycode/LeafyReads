from django.shortcuts import render, get_object_or_404
from books.models import Book, BookContent

def home(request, slug):
    book = get_object_or_404(Book, slug=slug)
    bookcontent = get_object_or_404(BookContent,book=book)
    
    return render(request, 'book.html', {'book': book,'bookcontent':bookcontent.content})

def library(request):
    books = Book.objects.all().order_by('-uploaded_at')
    return render(request,'library.html',{'books':books})