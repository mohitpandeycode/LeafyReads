from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from books.models import Book, BookContent, Genre, ReadLater,Like,ReadBy
from django.db.models import Count
from django.db import transaction


def home(request, slug):
    book = get_object_or_404(Book.objects.with_related(), slug=slug)

    if request.user.is_authenticated:
        def save_read():
            ReadBy.objects.get_or_create(user=request.user, book=book)
        transaction.on_commit(save_read)  # will run after response

    saved = (
        ReadLater.objects.filter(book=book, user=request.user).exists()
        if request.user.is_authenticated else False
    )
    liked = (
        Like.objects.filter(book=book, user=request.user).exists()
        if request.user.is_authenticated else False
    )

    return render(request, 'book.html', {
        'book': book,
        'bookcontent': book.content.content if hasattr(book, 'content') else '',
        'saved': saved,
        'liked': liked, 
    })




def library(request):
    books_list = (
        Book.objects
        .with_related()
        .defer('pdf_file', 'audio_file', 'price', 'isbn', 'updated_at')
        .order_by('-uploaded_at')
        .annotate(likes_count=Count('likes'))
        .annotate(readby_count=Count('readbooks'))
    )

    paginator = Paginator(books_list, 30)
    books = paginator.get_page(request.GET.get('page'))
    return render(request, 'library.html', {'books': books, 'title': "Library"})



#  BOOKS BY GENRE
def categories(request, slug):
    genre = get_object_or_404(Genre.objects.only('id', 'name', 'slug'), slug=slug)

    books_list = (
        Book.objects
        .filter(genre=genre)
        .select_related('genre', 'genre__category')
        .defer('pdf_file', 'audio_file', 'price', 'isbn', 'updated_at')
        .order_by('-uploaded_at')
    )

    paginator = Paginator(books_list, 30)
    books = paginator.get_page(request.GET.get('page'))

    return render(request, 'library.html', {
        'books': books,
        'title': f"{genre.name} Books",
        'category': f"of {genre.name} Books",
    })


#  USER WISHLIST
@login_required(login_url="/")
def myBooks(request):
    books_list = (
        Book.objects
        .filter(saved_by__user=request.user)
        .select_related('genre', 'genre__category')
        .defer('pdf_file', 'audio_file', 'price', 'isbn', 'updated_at')
        .order_by('title')
        .annotate(likes_count=Count('likes'))
        .annotate(readby_count=Count('readbooks'))
    )

    paginator = Paginator(books_list, 30)
    books = paginator.get_page(request.GET.get('page'))

    return render(request, 'library.html', {
        'books': books,
        'title': "Your Wishlist",
    })


#  SEARCH BOOKS (optimized fallback search)
def searchbooks(request):
    book_query = request.GET.get('search', '').strip()
    books_list = (
        Book.objects
        .select_related('genre', 'genre__category')
        .defer('pdf_file', 'audio_file', 'price', 'isbn', 'updated_at')
        .order_by('-uploaded_at')
    )

    if book_query:
        keywords = book_query.split()
        query = Q()
        for kw in keywords:
            query |= (
                Q(title__icontains=kw)
                | Q(author__icontains=kw)
                | Q(genre__name__icontains=kw)
                | Q(slug__icontains=kw)
            )
        books_list = books_list.filter(query).distinct()

    paginator = Paginator(books_list, 30)
    books = paginator.get_page(request.GET.get('page'))

    return render(request, 'library.html', {
        'books': books,
        'search': book_query,
        'title': f"Search results for '{book_query}'" if book_query else "All Books",
    })


#  ADD / REMOVE FROM READ LATER
@login_required
def toggle_read_later(request, book_slug):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    book = get_object_or_404(Book, slug=book_slug)
    obj, created = ReadLater.objects.get_or_create(user=request.user, book=book)

    if created:
        return JsonResponse({'status': 'saved', 'message': 'Book saved to Read Later'})
    obj.delete()
    return JsonResponse({'status': 'removed', 'message': 'Book removed from Read Later'})

@login_required
def toggle_like(request, book_slug):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    book = get_object_or_404(Book, slug=book_slug)
    like, created = Like.objects.get_or_create(user=request.user, book=book)

    if created:
        return JsonResponse({'status': 'liked', 'message': 'You Liked the book 🤩'})
    
    like.delete()
    return JsonResponse({'status': 'unliked', 'message': 'Like removed.'})
