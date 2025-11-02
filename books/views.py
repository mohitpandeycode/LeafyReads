from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from books.models import Book, BookContent, Genre, ReadLater, Like, ReadBy
from django.db.models import Count, OuterRef, Subquery, IntegerField
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.views.decorators.cache import cache_page




def home(request, slug):
    # Base queryset with related content
    book_qs = Book.objects.select_related("content")

    if request.user.is_authenticated:
        saved_subquery = ReadLater.objects.filter(
            book=OuterRef("pk"), user=request.user
        )
        liked_subquery = Like.objects.filter(book=OuterRef("pk"), user=request.user)

        book_qs = book_qs.annotate(
            is_saved=Exists(saved_subquery), is_liked=Exists(liked_subquery)
        )

    book = get_object_or_404(book_qs, slug=slug)
    if request.user.is_authenticated:

        def save_read():
            ReadBy.objects.get_or_create(user=request.user, book=book)

        transaction.on_commit(save_read)

    return render(
        request,
        "book.html",
        {
            "book": book,
            "bookcontent": getattr(book.content, "content", ""),
            "saved": getattr(book, "is_saved", False),
            "liked": getattr(book, "is_liked", False),
        },
    )

def library(request):
    recently_read_books = []
    if request.user.is_authenticated:
        recently_read_books = (
            ReadBy.objects.filter(user=request.user)
            .select_related("book")
            .only(
                "book__id",
                "book__title",
                "book__slug",
                "book__author",
                "book__cover_front",
                "readed_at",
            )
            .order_by("-readed_at")[:10]
        )

    likes_subquery = Subquery(
        Book.objects.filter(id=OuterRef("id"))
        .annotate(count=Count("likes"))
        .values("count")[:1],
        output_field=IntegerField(),
    )

    readby_subquery = Subquery(
        Book.objects.filter(id=OuterRef("id"))
        .annotate(count=Count("readbooks"))
        .values("count")[:1],
        output_field=IntegerField(),
    )

    books_list = (
        Book.objects.defer("content")
        .annotate(likes_count=likes_subquery, readby_count=readby_subquery)
        .order_by("-uploaded_at")
    )

    paginator = Paginator(books_list, 30)
    books = paginator.get_page(request.GET.get("page"))
    categories = Genre.objects.all().order_by("name")

    return render(
        request,
        "library.html",
        {
            "title": "Library",
            "books": books,
            "recently_read_books": recently_read_books,
            "categories": categories,
        },
    )


def categories(request, slug):
    current_genre = get_object_or_404(Genre, slug=slug)

    likes_subquery = Subquery(
        Book.objects.filter(id=OuterRef("id"))
        .annotate(count=Count("likes"))
        .values("count")[:1],
        output_field=IntegerField(),
    )

    readby_subquery = Subquery(
        Book.objects.filter(id=OuterRef("id"))
        .annotate(count=Count("readbooks"))
        .values("count")[:1],
        output_field=IntegerField(),
    )
    books_list = (
        Book.objects.filter(genre=current_genre)
        .annotate(likes_count=likes_subquery, readby_count=readby_subquery)
        .order_by("-uploaded_at")
    )

    paginator = Paginator(books_list, 30)
    books = paginator.get_page(request.GET.get("page"))

    all_categories = Genre.objects.all().order_by("name")

    return render(
        request,
        "library.html",
        {
            "books": books,
            "title": f"{current_genre.name} Books",
            "category": current_genre,
            "categories": all_categories,
        },
    )


@login_required(login_url="/")
def myBooks(request):
    books_qs = (
        Book.objects.filter(saved_by__user=request.user)
        .only("id", "title", "slug", "cover_front", "author")
        .annotate(
            likes_count=Count("likes", distinct=True),
            readby_count=Count("readbooks", distinct=True),
        )
        .order_by("title")
    )

    paginator = Paginator(books_qs, 30)
    books = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "library.html",
        {
            "books": books,
            "title": "Your Wishlist",
        },
    )


def searchbooks(request):
    book_query = request.GET.get("q", "").strip()

    books_list = (
        Book.objects.only("id", "title", "slug", "author", "cover_front")
        .annotate(
            likes_count=Count("likes", distinct=True),
            readby_count=Count("readbooks", distinct=True),
        )
        .order_by("-uploaded_at")
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
    books = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "library.html",
        {
            "books": books,
            "search": book_query,
            "title": (
                f"Search results for '{book_query}'" if book_query else "All Books"
            ),
        },
    )



def ajax_search(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        keywords = query.split()
        q_obj = Q()
        for kw in keywords:
            q_obj |= (
                Q(title__icontains=kw)
                | Q(author__icontains=kw)
                | Q(genre__name__icontains=kw)
                | Q(slug__icontains=kw)
            )

        books = (
            Book.objects.filter(q_obj)
            .only("id", "title", "slug", "author")[:8]
        )

        # Updated loop to return only the requested fields
        for b in books:
            results.append({
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "slug": b.slug,
            })

    return JsonResponse({"results": results})


@login_required
def toggle_read_later(request, book_slug):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )

    book = get_object_or_404(Book, slug=book_slug)
    obj, created = ReadLater.objects.get_or_create(user=request.user, book=book)

    if created:
        return JsonResponse({"status": "saved", "message": "Book saved to Read Later"})
    obj.delete()
    return JsonResponse(
        {"status": "removed", "message": "Book removed from Read Later"}
    )


@login_required
def toggle_like(request, book_slug):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )

    book = get_object_or_404(Book, slug=book_slug)
    like, created = Like.objects.get_or_create(user=request.user, book=book)

    if created:
        return JsonResponse({"status": "liked", "message": "You Liked the book 🤩"})

    like.delete()
    return JsonResponse({"status": "unliked", "message": "Like removed."})
