from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from books.models import Book, BookContent, Genre, ReadLater
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector  # for PostgreSQL full-text search


# BOOK DETAIL PAGE

def home(request, slug):

    book = get_object_or_404(
        Book.objects.select_related('genre').only('id', 'title', 'slug', 'genre_id', 'author'),
        slug=slug
    )
    bookcontent = get_object_or_404(BookContent.objects.only('content'), book=book)
    
    return render(request, 'book.html', {
        'book': book,
        'bookcontent': bookcontent.content
    })


# LIBRARY PAGE WITH PAGINATION

def library(request):
    books_list = Book.objects.select_related('genre').only('id','title','genre_id','uploaded_at','slug').order_by('-uploaded_at')
    paginator = Paginator(books_list, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    return render(request, 'library.html', {
        'books': books,
        'title': "The Books Library"
    })



# BOOKS BY CATEGORY

def categories(request, slug):
    # Fetch the category (genre) only
    category = get_object_or_404(Genre.objects.only('id','name','slug'), slug=slug)
    
    # Fetch books in that category with related genre
    books_list = Book.objects.filter(genre=category).select_related('genre').only(
        'id','title','slug','genre_id','uploaded_at'
    ).order_by('-uploaded_at')
    
    paginator = Paginator(books_list, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    return render(request, 'library.html', {
        'books': books,
        'title': f"{category.name} Books",
        'category': f"of {category.name} Books"
    })



# USER WISHLIST
@login_required(login_url="/")
def myBooks(request):
    books_list = ReadLater.objects.filter(user=request.user).select_related('book', 'book__genre').only(
        'id','book_id','book__title','book__genre_id','book__slug'
    ).order_by('id')
    
    paginator = Paginator(books_list, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    return render(request, 'library.html', {
        'books': books,
        'title': "Your Wishlist"
    })



# SEARCH BOOKS

def searchbooks(request):
    book_query = request.GET.get('search', '').strip()
    books_list = Book.objects.select_related('genre').only(
        'id','title','slug','author','genre_id','uploaded_at'
    ).order_by('-uploaded_at')

    if book_query:
        # books_list = books_list.annotate(
        #     search=SearchVector('title', 'author', 'genre__name')
        # ).filter(search=book_query)
        # Alternative for small datasets: fallback to Q objects
        keywords = book_query.split()
        query = Q()
        for keyword in keywords:
            query |= (Q(title__icontains=keyword) | Q(author__icontains=keyword) | Q(genre__name__icontains=keyword) | Q(slug__icontains=keyword))
        books_list = books_list.filter(query).distinct()

    paginator = Paginator(books_list, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    return render(request, 'library.html', {
        'books': books,
        'search': book_query,
        'title': f"Search results for '{book_query}'"
    })
