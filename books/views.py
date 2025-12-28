from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Count, F, OuterRef, Subquery, IntegerField, Exists
from django.db.models.functions import Coalesce
from django.core.cache import cache
from django.contrib.postgres.search import TrigramSimilarity
from django.utils.html import strip_tags
import hashlib
import random
from books.models import Book, BookContent, Genre, ReadLater, Like, ReadBy, SearchQueryLog

def home(request, slug):
    book_qs = Book.objects.select_related("content")
    if request.user.is_authenticated:
        saved_subquery = ReadLater.objects.filter(
            book=OuterRef("pk"), user=request.user
        )
        liked_subquery = Like.objects.filter(
            book=OuterRef("pk"), user=request.user
        )
        book_qs = book_qs.annotate(
            is_saved=Exists(saved_subquery), 
            is_liked=Exists(liked_subquery)
        )

    book = get_object_or_404(book_qs, slug=slug)

    # RECORD HISTORY (Async-safe)
    if request.user.is_authenticated:
        def save_read():
            ReadBy.objects.get_or_create(user=request.user, book=book)
        transaction.on_commit(save_read)

    # Book exists but has no Content yet.
    try:
        content_obj = book.content
        has_content = True
    except Exception:
        content_obj = None
        has_content = False

    # 5. DEVICE DETECTION & RENDERING
    pagination_context = None
    display_content = ""

    if request.user_agent.is_mobile:
        template_name = "mobileBook.html"
        if has_content:
            content_chunks = getattr(content_obj, "chunks", [])
        else:
            content_chunks = []

        # Paginate the pre-split chunks
        paragraphs_per_page = 30 
        paginator = Paginator(content_chunks, paragraphs_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Join only the paragraphs needed for THIS page
        display_content = "".join(page_obj.object_list)
        pagination_context = page_obj 

    else:
        template_name = "book.html"
        if has_content:
            display_content = getattr(content_obj, "content", "")

    return render(
        request,
        template_name,
        {
            "book": book,
            "bookcontent": display_content,
            "page_obj": pagination_context,
            "saved": getattr(book, "is_saved", False),
            "liked": getattr(book, "is_liked", False),
        },
    )



def openBook(request, slug):
    # 1. Reuseable Subqueries
    likes_sq = Like.objects.filter(book_id=OuterRef("pk")).values("book").annotate(c=Count("id")).values("c")
    saved_sq = ReadLater.objects.filter(book_id=OuterRef("pk")).values("book").annotate(c=Count("id")).values("c")
    reads_sq = ReadBy.objects.filter(book_id=OuterRef("pk")).values("book").annotate(c=Count("id")).values("c")

    # 2. Fetch Main Book
    book = get_object_or_404(
        Book.objects.select_related("genre", "genre__category")
        .annotate(
            likes_count=Coalesce(Subquery(likes_sq, output_field=IntegerField()), 0),
            saved_count=Coalesce(Subquery(saved_sq, output_field=IntegerField()), 0),
            read_count=Coalesce(Subquery(reads_sq, output_field=IntegerField()), 0),
        ),
        slug=slug,
        is_published=True,
    )

    # 3. Optimized Content
    content_data = BookContent.objects.filter(book=book).values("chunks").first()
    
    if content_data and content_data.get("chunks"):
        # Combine first 5 chunks to ensure we have enough text for 5 lines
        # Then strip tags and take first 1000 characters
        raw_text = " ".join(content_data["chunks"][:5])
        book.bookcontent = strip_tags(raw_text)[:1000]
    else:
        book.bookcontent = ""

    # 4. Related Books
    related_books = (
        Book.objects.select_related("genre")
        .filter(is_published=True, genre=book.genre)
        .exclude(id=book.id)
        .annotate(
            likes_count=Coalesce(Subquery(likes_sq, output_field=IntegerField()), 0),
            read_count=Coalesce(Subquery(reads_sq, output_field=IntegerField()), 0),
        )
        .order_by("-uploaded_at")
        .only("title", "slug", "cover_front", "genre", "uploaded_at")[:12]
    )

    # 5. User Flags
    user_saved = False
    if request.user.is_authenticated:
        user_saved = ReadLater.objects.filter(user=request.user, book=book).exists()

    return render(
        request,
        "bookDesc.html",
        {
            "title": book.title,
            "book": book,
            "related_books": related_books,
            "user_saved": user_saved,
        }
    )
  

def library(request):
    #Categories
    categories = cache.get("library_categories")

    if categories is None:
        categories = list(Genre.objects.all())
        cache.set("library_categories", categories, timeout=60 * 60 * 24)

    categories = categories[:]
    random.shuffle(categories)

    #Main Books List (Paginated Cache: 15 mins) ---
    # We must include the page number in the cache key!
    page_number = request.GET.get("page", 1)
    books_cache_key = f"library_books_page_{page_number}"
    
    books = cache.get(books_cache_key)
    if books is None:
        # complex query logic
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
        books = paginator.get_page(page_number)
        
        # Cache the specific page result
        cache.set(books_cache_key, books, timeout=60 * 15)

    #Recently Read (User-Specific Cache: 1 hour) ---
    recently_read_books = []
    if request.user.is_authenticated:
        user_recent_key = f"library_recent_user_{request.user.id}"
        recently_read_books = cache.get(user_recent_key)
        
        if recently_read_books is None:
            recently_read_books = list(
                ReadBy.objects.filter(user=request.user)
                .select_related("book")
                .only(
                    "book__id", "book__title", "book__slug",
                    "book__author", "book__cover_front", "readed_at",
                )
                .order_by("-readed_at")[:10]
            )
            cache.set(user_recent_key, recently_read_books, timeout=60 * 60)

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
        "readlater.html",
        {
            "books": books,
            "title": "Your Wishlist",
        },
    )


def searchbooks(request):
    book_query = request.GET.get("q", "").strip()
    page_number = request.GET.get("page", 1)

    # 1. Full Page Cache Check
    cache_key = f"search_{book_query}_page_{page_number}"
    context = cache.get(cache_key)

    if context:
        return render(request, "library.html", context)

    # 2. Define Subqueries
    likes_subquery = Subquery(
        Book.objects.filter(id=OuterRef("id"))
        .annotate(cnt=Count("likes"))
        .values("cnt")[:1],
        output_field=IntegerField()
    )
    
    readby_subquery = Subquery(
        Book.objects.filter(id=OuterRef("id"))
        .annotate(cnt=Count("readbooks"))
        .values("cnt")[:1],
        output_field=IntegerField()
    )
    
    # 3. Cached Suggestions
    cached_suggestions = cache.get("popular_books_sidebar")
    
    if not cached_suggestions:
        cached_suggestions = list(
            Book.objects.filter(is_published=True).only(
                "id", "title", "slug", "author", "cover_front"
            ).annotate(
                likes_count=likes_subquery,
                readby_count=readby_subquery 
            ).order_by('-likes_count')[:12]
        )
        cache.set("popular_books_sidebar", cached_suggestions, 3600)

    # 4. Main Query Setup
    books_queryset = Book.objects.filter(is_published=True).select_related("genre").only(
        "id", "title", "slug", "author", "cover_front", "genre__name", "uploaded_at"
    )

    suggested_books = None
    no_results_found = False

    if book_query:
        # --- Trigram Search Logic ---
        books_queryset = books_queryset.annotate(
            similarity=(
                TrigramSimilarity('title', book_query) * 1.0 +
                TrigramSimilarity('author', book_query) * 0.7 +
                TrigramSimilarity('slug', book_query) * 0.5 +
                TrigramSimilarity('genre__name', book_query) * 0.5
            )
        ).filter(
            # Allow EITHER good similarity OR exact substring match
            Q(similarity__gt=0.1) | 
            Q(slug__icontains=book_query) | 
            Q(title__icontains=book_query)
        ).order_by('-similarity', '-uploaded_at')

        # Attach counts
        books_queryset = books_queryset.annotate(
            likes_count=likes_subquery, 
            readby_count=readby_subquery
        )

        paginator = Paginator(books_queryset, 30)
        books = paginator.get_page(page_number)

        if len(books) == 0:
            no_results_found = True
            
            try:
                clean_query = book_query.lower().strip()[:200]
                if clean_query:
                    SearchQueryLog.objects.update_or_create(
                        query=clean_query,
                        defaults={'count': F('count') + 1}
                    )
            except Exception:
                pass

            suggested_books = cached_suggestions
        
        else:
            suggested_books = cached_suggestions

    else:
        # No Search
        books_queryset = books_queryset.order_by("-uploaded_at").annotate(
            likes_count=likes_subquery, 
            readby_count=readby_subquery
        )
        paginator = Paginator(books_queryset, 30)
        books = paginator.get_page(page_number)

    context = {
        "books": books,
        "search": book_query,
        "title": f"Results for '{book_query}'" if book_query else "All Books",
        "no_results_found": no_results_found,
        "suggested_books": suggested_books,
    }
    
    cache.set(cache_key, context, timeout=60 * 2)

    return render(request, "library.html", context)


# AJAX Search with Caching and Concurrency Control
def ajax_search(request):
    # 1. Clean the input
    query = request.GET.get("q", "").strip()[:100].lower()

    # 2. LIMIT CHECK: If length is less than 3, return empty (Safety)
    if len(query) < 3:
        return JsonResponse({"results": []})
        
    # 3. Cache Check
    safe_query = hashlib.md5(query.encode('utf-8')).hexdigest()
    cache_key = f"ajax_search_{safe_query}"
    cached_results = cache.get(cache_key)
    
    if cached_results:
        return JsonResponse({"results": cached_results})

    # 4. Build Query
    keywords = query.split()
    q_obj = Q()
    for kw in keywords:
        q_obj |= (
            Q(title__icontains=kw)
            | Q(slug__icontains=kw)
            | Q(author__icontains=kw)
            | Q(genre__name__icontains=kw) 
        )

    # 5. Fetch from DB
    books = list(
        Book.objects.filter(q_obj, is_published=True)
        .only("id", "title", "author", "slug") 
        .order_by('-uploaded_at')[:20] 
    )

    # 6. Smart Sorting (Exact matches first)
    books.sort(key=lambda x: x.title.lower().startswith(query), reverse=True)

    # 7. Serialize
    results = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "slug": b.slug,
        }
        for b in books[:8]
    ]
    # 8. Set Cache
    cache.set(cache_key, results, timeout=300)
    
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
