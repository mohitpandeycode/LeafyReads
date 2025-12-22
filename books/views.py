from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch, Count, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from books.models import Book, BookContent, Genre, ReadLater, Like, ReadBy,SearchQueryLog
from django.db.models import Count, OuterRef, Subquery, IntegerField
from django.db import transaction
from django.db.models import Exists, OuterRef,Subquery, Value
from django.db.models.functions import Substr, Coalesce
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.contrib.postgres.search import TrigramSimilarity
from django.utils.html import strip_tags
import hashlib
import time

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
        categories = list(Genre.objects.all().order_by("name"))
        cache.set("library_categories", categories, timeout=60 * 60 * 24)

    #Main Books List (Paginated Cache: 15 mins) ---
    # We must include the page number in the cache key!
    page_number = request.GET.get("page", 1)
    books_cache_key = f"library_books_page_{page_number}"
    
    books = cache.get(books_cache_key)
    if books is None:
        # Your existing complex query logic
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

    cache_key = f"search_{book_query}_page_{page_number}"
    context = cache.get(cache_key)

    if context:
        return render(request, "library.html", context)

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

    books_queryset = Book.objects.select_related("genre").only(
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
                TrigramSimilarity('genre__name', book_query) * 0.6+
                TrigramSimilarity('slug', book_query) * 0.4
            )
        ).filter(similarity__gt=0.1).order_by('-similarity', '-uploaded_at')

        # Attach the counts ONLY to the final filtered list
        books_queryset = books_queryset.annotate(
            likes_count=likes_subquery, 
            readby_count=readby_subquery
        )

        paginator = Paginator(books_queryset, 30)
        books = paginator.get_page(page_number)

        # Check Python list length (No extra DB call)
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

            # Fetch suggestions only if needed
            suggested_books = Book.objects.only(
                "id", "title", "slug", "author", "cover_front"
            ).annotate(
                likes_count=likes_subquery
            ).order_by('-likes_count')[:12]
        
        else:
            suggested_books = Book.objects.only(
                "id", "title", "slug", "author", "cover_front"
            ).annotate(
                likes_count=likes_subquery
            ).order_by('-likes_count')[:12]

    else:
        # No Search - Just latest books
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
LOCK_TIMEOUT = 5
WAIT_DELAY = 0.1

def ajax_search(request):
    query = request.GET.get("q", "").strip().lower()
    
    if not query:
        return JsonResponse({"results": []})
        
    safe_query = hashlib.md5(query.encode('utf-8')).hexdigest()
    cache_key = f"search_results_{safe_query}"
    lock_key = f"{cache_key}_lock"

    # 1. Try to fetch results from Redis cache
    cached_results = cache.get(cache_key)
    if cached_results is not None:
        return JsonResponse({"results": cached_results})

    # 2. CACHE MISS! Attempt to acquire a lock (Concurrency control)
    if cache.add(lock_key, 'true', timeout=LOCK_TIMEOUT):
        
        results = []
        try:
            # Build the query
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
                .only("id", "title", "slug", "author", "genre_id") 
                .select_related("genre") 
                [:8]
            )

            # Serialize results
            for b in books:
                results.append({
                    "id": b.id,
                    "title": b.title,
                    "author": b.author,
                    "slug": b.slug,
                })
            
            # Populate cache and return
            cache.set(cache_key, results, timeout=120)
            return JsonResponse({"results": results})
        finally:
            # Release the lock
            cache.delete(lock_key)
            
    else:
        # 3. LOCK UNAVAILABLE: Wait and retry cache lookup
        time.sleep(WAIT_DELAY) 
        final_results = cache.get(cache_key)
        
        if final_results is not None:
            return JsonResponse({"results": final_results})
        else:
            return JsonResponse({"results": []})

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
