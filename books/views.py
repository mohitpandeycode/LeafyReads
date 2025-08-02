from django.shortcuts import render, get_object_or_404
from books.models import Book, BookContent, Genre, ReadLater
from django.db.models import Q

def home(request, slug):
    # Use select_related to fetch related genre in one query if needed in template
    book = get_object_or_404(Book.objects.select_related('genre'), slug=slug)
    # Use only() to limit fields if possible
    bookcontent = get_object_or_404(BookContent.objects.only('content'), book=book)
    return render(request, 'book.html', {'book': book, 'bookcontent': bookcontent.content})

def library(request):
    # Use select_related to fetch related genre in one query for all books
    books = Book.objects.select_related('genre').all().order_by('-uploaded_at')
    context = {
        'books': books,
        'title': "The books Library"
    }
    return render(request, 'library.html', context)

def categories(request, slug):
    # Use select_related to fetch related category in one query
    category = get_object_or_404(Genre.objects.select_related('category'), slug=slug)
    books = Book.objects.filter(genre=category).select_related('genre').order_by('-uploaded_at')
    context = {
        'books': books,
        'title': f"{category.name} Books",
        'category': f" of {category.name} Books"
    }
    return render(request, 'library.html', context)

def myBooks(request):
    # Use select_related to fetch related book and genre in one query
    books = ReadLater.objects.filter(user=request.user).select_related('book', 'book__genre')
    context = {
        'books': books,
        'title': "Your Wishlist",
    }
    return render(request, 'library.html', context)

def searchbooks(request):
    book_query = request.GET.get('search', '').strip()
    books = Book.objects.select_related('genre').all().order_by('-uploaded_at')

    if book_query:
        keywords = book_query.split()
        # Use reduce to build Q object more efficiently
        query = Q()
        for keyword in keywords:
            q = (
                Q(title__icontains=keyword) |
                Q(author__icontains=keyword) |
                Q(genre__name__icontains=keyword) |
                Q(slug__icontains=keyword)
            )
            query |= q
        books = books.filter(query).distinct()

    context = {
        'books': books,
        'search': book_query,
        'title': f"Search result of {book_query} Books",
    }
    return render(request, 'library.html', context)