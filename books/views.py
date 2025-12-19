from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch, Count, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from books.models import Book, BookContent, Genre, ReadLater, Like, ReadBy
from django.db.models import Count, OuterRef, Subquery, IntegerField
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.contrib.postgres.search import TrigramSimilarity
import hashlib
import time



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

    # --- DEVICE DETECTION & PAGINATION ---
    full_content = getattr(book.content, "content", "")
    
    if request.user_agent.is_mobile:
        template_name = "mobileBook.html"
        
        # 1. Turn the long string into a list of paragraphs
        # We split by '</p>' and add it back to maintain valid HTML
        # The 'if p.strip()' removes any empty chunks
        content_chunks = [p + '</p>' for p in full_content.split('</p>') if p.strip()]

        # 2. Setup Paginator
        # 'paragraphs_per_page' controls how long a page is. 
        # Adjust '3' to '5' or '2' depending on how long your paragraphs usually are.
        paragraphs_per_page = 20 
        paginator = Paginator(content_chunks, paragraphs_per_page)

        # 3. Get the current page number from the URL (e.g., ?page=2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # 4. Join the list of paragraphs back into a string to display
        # We override the 'bookcontent' variable just for this mobile view
        display_content = "".join(page_obj.object_list)
        
        # We pass 'page_obj' to context so the template can show Next/Prev buttons
        pagination_context = page_obj 

    else:
        # Desktop view: No pagination, show everything
        template_name = "book.html"
        display_content = full_content
        pagination_context = None

    return render(
        request,
        template_name,
        {
            "book": book,
            "bookcontent": display_content, # Contains only the current page's text on mobile
            "page_obj": pagination_context, # Needed for Next/Prev buttons
            "saved": getattr(book, "is_saved", False),
            "liked": getattr(book, "is_liked", False),
        },
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
        "library.html",
        {
            "books": books,
            "title": "Your Wishlist",
        },
    )

def searchbooks(request):
    book_query = request.GET.get("q", "").strip()

    books_list = (
        Book.objects
        # Fetch necessary fields to prevent extra DB calls
        .only("id", "title", "slug", "author", "cover_front", "genre_id")
        .annotate(
            likes_count=Count("likes", distinct=True),
            readby_count=Count("readbooks", distinct=True),
        )
    )

    if book_query:
        # Multi-Field Trigram Search
        # calculate similarity for ALL 3 fields and sum them up.
        books_list = books_list.annotate(
            similarity=(
                TrigramSimilarity('title', book_query) * 1.0 +   # Highest weight
                TrigramSimilarity('author', book_query) * 0.7 +  # Medium weight
                TrigramSimilarity('slug', book_query) * 0.5      # Lower weight
            )
        )
        
        # Filter results that have ANY similarity (> 0.1 is very broad/permissive)
        # This replaces the slow 'icontains' loop.
        books_list = books_list.filter(similarity__gt=0.1)
        
        # Order by Best Match first, then by Newest
        books_list = books_list.order_by('-similarity', '-uploaded_at')

    else:
        # Default ordering
        books_list = books_list.order_by("-uploaded_at")

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
