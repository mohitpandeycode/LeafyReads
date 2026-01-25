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
from django.utils import timezone
from datetime import timedelta
from books.models import Book, BookContent, Genre, ReadLater, Like, ReadBy, SearchQueryLog
#  Language choice to filter language based books

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Hindi', 'Hindi'),
    ('Arabic', 'Arabic'),
    ('Bengali', 'Bengali'),
    ('Chinese', 'Chinese'),
    ('French', 'French'),
    ('German', 'German'),
    ('Gujarati', 'Gujarati'),
    ('Japanese', 'Japanese'),
    ('Kannada', 'Kannada'),
    ('Malayalam', 'Malayalam'),
    ('Marathi', 'Marathi'),
    ('Odia', 'Odia'),
    ('Portuguese', 'Portuguese'),
    ('Punjabi', 'Punjabi'),
    ('Russian', 'Russian'),
    ('Sanskrit', 'Sanskrit'),
    ('Spanish', 'Spanish'),
    ('Tamil', 'Tamil'),
    ('Telugu', 'Telugu'),
    ('Urdu', 'Urdu')
]

def apply_common_filters(queryset, lang_param, sort_param):
    """Applies Language and Sort filters to any Book QuerySet"""
    
    # 1. Language Filter
    if lang_param:
        queryset = queryset.filter(book_language__iexact=lang_param)
        
    # 2. Sorting
    if sort_param == 'popular':
        queryset = queryset.order_by('-likes_count', '-uploaded_at')
    elif sort_param == 'views':
        queryset = queryset.order_by('-views_count', '-uploaded_at')
    elif sort_param == 'oldest':
        queryset = queryset.order_by('uploaded_at')
    
    return queryset


def home(request, slug):
    book_id = Book.objects.filter(slug=slug).values_list('id', flat=True).first()
    
    if book_id:
        # CONFIGURATION of hours here
        VIEW_COOLDOWN_HOURS = 3 
        
        # Create a unique session key for this specific book
        session_key = f'viewed_book_{book_id}_last_at'
        last_view_str = request.session.get(session_key)
        
        should_increment = False

        if not last_view_str:
            # Case 1: User has NEVER viewed this book (or cleared cookies)
            should_increment = True
        else:
            # Case 2: User viewed before. Check if X hours have passed.
            try:
                last_view_time = timezone.datetime.fromisoformat(last_view_str)
                if timezone.now() > last_view_time + timedelta(hours=VIEW_COOLDOWN_HOURS):
                    should_increment = True
            except ValueError:
                # If the session data is weird/corrupt, reset it
                should_increment = True

        if should_increment:
            # Increment DB Counter efficiently using F() expression
            Book.objects.filter(id=book_id).update(views_count=F('views_count') + 1)
            
            # Update Session Timestamp to NOW
            request.session[session_key] = timezone.now().isoformat()
            request.session.modified = True

    # --- 2. FETCH BOOK & USER DATA ---
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

    # --- 3. RECORD HISTORY (Async-safe) ---
    if request.user.is_authenticated:
        def save_read():
            ReadBy.objects.get_or_create(user=request.user, book=book)
        transaction.on_commit(save_read)

    # --- 4. CONTENT HANDLING ---
    try:
        content_obj = book.content
        has_content = True
    except Exception:
        content_obj = None
        has_content = False

    # --- 5. DEVICE DETECTION & RENDERING ---
    pagination_context = None
    display_content = ""

    if request.user_agent.is_mobile:
        template_name = "mobileBook.html"
        content_chunks = getattr(content_obj, "chunks", []) if has_content else []

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
            "title": book.title
        },
    )
    
    
# ISOLATED Scroll View (For PC "Normal View")
def book_page_view(request, slug):

    book_id = Book.objects.filter(slug=slug).values_list('id', flat=True).first()
    
    if book_id:
        # CONFIGURATION: Cooldown time in hours
        VIEW_COOLDOWN_HOURS = 3 
        
        # Unique session key
        session_key = f'viewed_book_{book_id}_last_at'
        last_view_str = request.session.get(session_key)
        
        should_increment = False

        if not last_view_str:
            # Case 1: First visit
            should_increment = True
        else:
            # Case 2: Check if X hours have passed
            try:
                last_view_time = timezone.datetime.fromisoformat(last_view_str)
                if timezone.now() > last_view_time + timedelta(hours=VIEW_COOLDOWN_HOURS):
                    should_increment = True
            except ValueError:
                should_increment = True

        if should_increment:
            # Increment DB Counter efficiently
            Book.objects.filter(id=book_id).update(views_count=F('views_count') + 1)
            
            # Update Session Timestamp
            request.session[session_key] = timezone.now().isoformat()
            request.session.modified = True

    # --- 2. MAIN DATA FETCHING ---
    book_qs = Book.objects.select_related("content")
    
    if request.user.is_authenticated:
        saved_subquery = ReadLater.objects.filter(book=OuterRef("pk"), user=request.user)
        liked_subquery = Like.objects.filter(book=OuterRef("pk"), user=request.user)
        book_qs = book_qs.annotate(is_saved=Exists(saved_subquery), is_liked=Exists(liked_subquery))

    book = get_object_or_404(book_qs, slug=slug)

    # --- 3. HISTORY RECORDING ---
    if request.user.is_authenticated:
        def save_read():
            ReadBy.objects.get_or_create(user=request.user, book=book)
        transaction.on_commit(save_read)

    # --- 4. CONTENT & PAGINATION (Strictly Chunk/Scroll based) ---
    try:
        content_obj = book.content
        content_chunks = getattr(content_obj, "chunks", []) if content_obj else []
    except:
        content_chunks = []

    paginator = Paginator(content_chunks, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    display_content = "".join(page_obj.object_list)

    # --- 5. RENDER ---
    return render(request, "mobileBook.html", {
        "book": book,
        "bookcontent": display_content,
        "page_obj": page_obj,
        "saved": getattr(book, "is_saved", False),
        "liked": getattr(book, "is_liked", False),
        "title": book.title,
        "view_mode": "page view" 
    })



def openBook(request, slug):
    # 1. Fetch Book
    book = get_object_or_404(
        Book.objects.select_related("genre", "genre__category"),
        slug=slug,
        is_published=True,
    )

    # 2. Optimized Content Fetching
    content_data = BookContent.objects.filter(book=book).values("chunks").first()
    
    if content_data and content_data.get("chunks"):
        raw_text = " ".join(content_data["chunks"][:5])
        book.bookcontent = strip_tags(raw_text)[:1000]
    else:
        book.bookcontent = ""
    # 3. Related Books
    related_books = (
        Book.objects.select_related("genre")
        .filter(is_published=True, genre=book.genre)
        .exclude(id=book.id)
        .only("title", "slug", "cover_front", "genre", "uploaded_at", "likes_count", "views_count")
        .order_by("-uploaded_at")[:12]
    )

    # 4. User Flags (Has the user saved this)
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
    categories = cache.get("library_categories")
    if categories is None:
        categories = list(Genre.objects.all())
        cache.set("library_categories", categories, timeout=60 * 60 * 24)

    categories = categories[:]
    random.shuffle(categories)

    # 1. Get Parameters
    page_number = request.GET.get("page", 1)
    sort_param = request.GET.get("sort", "newest") 
    lang_param = request.GET.get("lang", "").strip()

    # 2. Build Cache Key (Includes filters)
    books_cache_key = f"library_books_p{page_number}_s{sort_param}_l{lang_param}"
    
    books = cache.get(books_cache_key)
    
    if books is None:
        books_queryset = Book.objects.defer("content").filter(is_published=True)
        
        # 3. Apply Common Filters
        books_queryset = apply_common_filters(books_queryset, lang_param, sort_param)
        
        # Default Sort
        if sort_param == 'newest':
            books_queryset = books_queryset.order_by('-uploaded_at')

        paginator = Paginator(books_queryset, 30)
        books = paginator.get_page(page_number)
        
        cache.set(books_cache_key, books, timeout=60 * 15)

    recently_read_books = []
    if request.user.is_authenticated:
        user_recent_key = f"library_recent_user_{request.user.id}"
        recently_read_books = cache.get(user_recent_key)
        
        if recently_read_books is None:
            recently_read_books = list(
                ReadBy.objects.filter(user=request.user)
                .select_related("book")
                .order_by("-readed_at")[:10]
            )
            cache.set(user_recent_key, recently_read_books, timeout=60 * 60)

    return render(
        request,
        "library.html",
        {
            "title": "Digital Library",
            "books": books,
            "recently_read_books": recently_read_books,
            "categories": categories,
            "languages": LANGUAGE_CHOICES,
        },
    )



def categories(request, slug):
    current_genre = get_object_or_404(Genre, slug=slug)
    
    # 1. Get Parameters
    page_number = request.GET.get("page", 1)
    sort_param = request.GET.get("sort", "newest") 
    lang_param = request.GET.get("lang", "").strip()

    # 2. Base Query
    books_queryset = Book.objects.filter(genre=current_genre, is_published=True)

    # 3. Apply Common Filters
    books_queryset = apply_common_filters(books_queryset, lang_param, sort_param)

    # Default sort
    if sort_param == 'newest':
        books_queryset = books_queryset.order_by("-uploaded_at")

    paginator = Paginator(books_queryset, 30)
    books = paginator.get_page(page_number)

    all_categories = Genre.objects.all().order_by("name")
    return render(
        request,
        "library.html",
        {
            "books": books,
            "title": f"{current_genre.name} Books",
            "category": current_genre,
            "categories": all_categories,
            "languages": LANGUAGE_CHOICES,
        },
    )

@login_required(login_url="/")
def myBooks(request):
    books_qs = (
        Book.objects.filter(saved_by__user=request.user)
        .only("id", "title", "slug", "cover_front", "author", "likes_count", "views_count")
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
    
    # 1. Get Parameters
    sort_param = request.GET.get("sort", "relevance") 
    lang_param = request.GET.get("lang", "").strip()

    # 2. Update Cache Key
    cache_key = f"search_{book_query}_p{page_number}_s{sort_param}_l{lang_param}"
    context = cache.get(cache_key)
    
    if context:
        return render(request, "library.html", context)

    # Sidebar
    cached_suggestions = cache.get("popular_books_sidebar")
    if not cached_suggestions:
        cached_suggestions = list(
            Book.objects.filter(is_published=True)
            .only("id", "title", "slug", "author", "cover_front", "likes_count", "views_count", "is_published")
            .order_by('-likes_count')[:12]
        )
        cache.set("popular_books_sidebar", cached_suggestions, 3600)

    suggested_books = None
    no_results_found = False
    
    # Base Query
    books_queryset = Book.objects.filter(is_published=True).select_related("genre").only(
        "id", "title", "slug", "author", "cover_front", "genre__name", "uploaded_at",
        "likes_count", "views_count", "is_published", "book_language"
    )

    if book_query:
        # Search Logic
        books_queryset = books_queryset.annotate(
            similarity=(
                TrigramSimilarity('title', book_query) * 1.0 +
                TrigramSimilarity('author', book_query) * 0.8 +
                TrigramSimilarity('genre__name', book_query) * 0.6 +
                TrigramSimilarity('slug', book_query) * 0.5
            )
        ).filter(
            similarity__gt=0.05  
        )
        
        # 3. Apply Common Filters
        books_queryset = apply_common_filters(books_queryset, lang_param, sort_param)

        # 4. Sorting (Search Specific)
        if sort_param == 'popular':
            books_queryset = books_queryset.order_by('-likes_count')
        elif sort_param == 'views':
            books_queryset = books_queryset.order_by('-views_count')
        elif sort_param == 'oldest':
            books_queryset = books_queryset.order_by('uploaded_at')
        elif sort_param == 'newest':
            books_queryset = books_queryset.order_by('-uploaded_at')
        else:
            # Default: Relevance
            books_queryset = books_queryset.order_by('-similarity', '-likes_count')

        paginator = Paginator(books_queryset, 30)
        books = paginator.get_page(page_number)

        if len(books) == 0:
            no_results_found = True
            try:
                clean_query = book_query.lower().strip()[:200]
                if clean_query and len(clean_query) > 2:
                    SearchQueryLog.objects.update_or_create(
                        query=clean_query, defaults={'count': F('count') + 1}
                    )
            except Exception:
                pass
            suggested_books = cached_suggestions
        else:
            suggested_books = cached_suggestions

    else:
        # No Search provided - treat like Library
        books_queryset = apply_common_filters(books_queryset, lang_param, sort_param)
        if sort_param == 'relevance' or sort_param == 'newest':
             books_queryset = books_queryset.order_by("-uploaded_at")

        paginator = Paginator(books_queryset, 30)
        books = paginator.get_page(page_number)
        suggested_books = cached_suggestions

    context = {
        "books": books,
        "search": book_query,
        "title": f"Results for '{book_query}'" if book_query else "All Books",
        "no_results_found": no_results_found,
        "suggested_books": suggested_books,
        "languages": LANGUAGE_CHOICES,
    }
    
    cache.set(cache_key, context, timeout=60 * 2)

    return render(request, "library.html", context)

# AJAX Search with Caching and Concurrency Control
def ajax_search(request):
    # 1. Clean the input
    query = request.GET.get("q", "").strip()[:100].lower()

    if len(query) < 2:
        return JsonResponse({"results": []})
        
    safe_query = hashlib.md5(query.encode('utf-8')).hexdigest()
    cache_key = f"ajax_search_{safe_query}"
    cached_results = cache.get(cache_key)
    
    if cached_results:
        return JsonResponse({"results": cached_results})

    
    books = list(
        Book.objects.filter(is_published=True)
        .annotate(
            similarity=(
                # Weighted search: Title matches are most important
                TrigramSimilarity('title', query) * 1.0 +
                TrigramSimilarity('author', query) * 0.8 +
                TrigramSimilarity('slug', query) * 0.5 +
                TrigramSimilarity('genre__name', query) * 0.5
            )
        )
        .filter(
            similarity__gt=0.05 
        )
        .only("id", "title", "author", "slug") 
        .order_by(
            '-similarity',
            '-likes_count'   
        )[:8] # Limit to 8 for the dropdown
    )

    # 5. Serialize
    results = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "slug": b.slug,
        }
        for b in books
    ]
    
    # 6. Set Cache (Short duration for autocomplete: 5 mins)
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
