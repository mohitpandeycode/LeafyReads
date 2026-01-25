from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from books.models import Genre, Book, BookContent
from books.models import ReadBy, ReadLater, Review,Book,User
from userSection.forms import UserBookForm, BookContentForm
from django.core.paginator import Paginator
from community.models import Post, PostImage,Comment
from django.contrib import messages
from django.db.models import Count, Exists, OuterRef
from django.db.models import Q
from home.models import Notification,ContentType

@login_required
def profilepage(request):
    user = request.user
    stats = User.objects.filter(id=user.id).aggregate(
        books_read_count=Count('readby', distinct=True),
        read_later_count=Count('saved_books', distinct=True),
        
        # Existing Review Count
        reviews_count=Count('reviews', distinct=True),

        # NEW: Count Community Posts using related_name='posts'
        community_posts_count=Count('posts', distinct=True), 

        published_books_count=Count('uploaded_books', filter=Q(uploaded_books__is_published=True), distinct=True)
    )

    # 2.Fetch books + genre in ONE query
    recently_read_books = (
        ReadBy.objects.filter(user=user)
        .select_related("book", "book__genre") 
        .order_by("-readed_at")[:4]
    )

    context = {
        "profile_user": user,
        "recently_read_books": recently_read_books,
        **stats, # This now includes 'community_posts_count'
    }

    return render(request, "profilePage.html", context)

@login_required(login_url="/")
def readBooks(request):
    # 1.Get history entries for this user
    read_list = ReadBy.objects.filter(user=request.user).select_related('book').order_by('-readed_at')

    paginator = Paginator(read_list,28)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'read_books.html', {'books': page_obj})



@login_required(login_url="/")
def createBook(request):
    genres = Genre.objects.all()

    if request.method == "POST":
        book_form = UserBookForm(request.POST, request.FILES)
        content_form = BookContentForm(request.POST, request.FILES)

        if book_form.is_valid() and content_form.is_valid():
            
            # 1. Prepare Book Instance (In Memory)
            book = book_form.save(commit=False)
            book.uploaded_by = request.user
            book.author = request.user.get_full_name() or request.user.username
            
            # 2. Configure Status based on Action
            action = request.POST.get("action")
            
            if action == "save":
                book.is_draft = False 
                book.is_published = False
                redirect_url = "draftBooks"
                success_message = f'We have started reviewing your book "{book.title}". You will be notified once it is published to the community.'
                
            elif action == "continue":
                book.is_draft = True
                book.is_published = False
                redirect_url = None 
                success_message = f'"{book.title}" saved to draft. You can continue editing.'

            # 3. SAVE THE BOOK FIRST
            # This generates the ID needed for the notification below.
            book.save() 

            # 4. Create Notification
            if action == "save":
                Notification.objects.create(
                    recipient=request.user,
                    notification_type='book_review',
                    message=f'Your book <strong>{book.title}</strong> has been submitted for review. You will be notified once it is published to the community.',
                    content_type=ContentType.objects.get_for_model(Book),
                    object_id=book.id
                )
                
            elif action == "continue":
                Notification.objects.create(
                    recipient=request.user,
                    notification_type='draft_saved',
                    message=f'Your book <strong>{book.title}</strong> successfully saved to Drafts. You can continue editing. ',
                    content_type=ContentType.objects.get_for_model(Book),
                    object_id=book.id
                )

            # 5. Save Content
            bookcontent = content_form.save(commit=False)
            bookcontent.book = book
            bookcontent.save() 

            # 6. Final Redirect
            messages.success(request, success_message)
            
            if action == "continue":
                return redirect("updateUserBook", slug=book.slug)
            else:
                return redirect(redirect_url)

        else:
            messages.error(request, "Please add the required fields (Title, Cover Image, Content).")
    
    else:
        book_form = UserBookForm()
        content_form = BookContentForm()

    return render(request, "create_book.html", {
        "book_form": book_form,  
        "content_form": content_form, 
        "genres": genres
    })



@login_required(login_url="/") 
def updateUserBook(request, slug):
    book = get_object_or_404(Book, slug=slug, uploaded_by=request.user)
    bookcontent, created = BookContent.objects.get_or_create(book=book)
    # Find all unread notifications for THIS user regarding THIS specific book
    book_content_type = ContentType.objects.get_for_model(Book)
    Notification.objects.filter(
        recipient=request.user,
        content_type=book_content_type,
        object_id=book.id,
        is_read=False
    ).update(is_read=True)

    if request.method == "POST":
        book_form = UserBookForm(request.POST, request.FILES, instance=book)
        content_form = BookContentForm(request.POST, request.FILES, instance=bookcontent)

        if book_form.is_valid() and content_form.is_valid():
            
            # 1. Capture Action
            action = request.POST.get("action")
            
            # 2. Prepare Book & Status
            book = book_form.save(commit=False)
            
            if action == "save":
                book.is_draft = False
                # Reset published status if they edit a live book and re-submit
                book.is_published = False 
                success_message = f'We have started reviewing your book "{book.title}". You will be notified once it is published to the community.'
                
            elif action == "continue":
                book.is_draft = True
                book.is_published = False
                success_message = "Saved to drafts. Make sure to Publish it once done."
    
            # 3. SAVE BOOK (Ensures status is updated in DB)
            book.save() 
            
            # 4. Create Notification
            if action == "save":
                Notification.objects.create(
                    recipient=request.user,
                    notification_type='book_review',
                    message=f'Your book <strong>{book.title}</strong> has been submitted for review. You will be notified once it is published to the community.',
                    content_type=ContentType.objects.get_for_model(Book),
                    object_id=book.id
                )
            
            # 5. Save Content
            if content_form.has_changed():
                content = content_form.save(commit=False)
                content.save() 

            # 6. Redirect
            messages.success(request, success_message)
            
            if action == "save":
                return redirect("draftBooks")
            elif action == "continue":
                return redirect("updateUserBook", slug=book.slug)

    else:
        book_form = UserBookForm(instance=book)
        content_form = BookContentForm(instance=bookcontent)

    return render(request, "update_book.html", {
        "book_form": book_form,
        "content_form": content_form,
        "book": book,
    })
    
def draftBooks(request):
    books_queryset = Book.objects.filter(uploaded_by=request.user).select_related('genre').order_by('-uploaded_at')
    # --- HANDLE SEARCH ---
    search_query = request.GET.get('search', '')
    if search_query:
        books_queryset = books_queryset.filter(
            Q(title__icontains=search_query) |
            Q(slug__icontains=search_query) |
            Q(genre__name__icontains=search_query)
        )

    # --- HANDLE BULK ACTIONS (Delete) ---
    if request.method == "POST":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_books")

        if action == "delete" and selected_ids:
            deleted_count, _ = Book.objects.filter(
                id__in=selected_ids, 
                uploaded_by=request.user
            ).delete()
            
            messages.success(request, f"Successfully deleted.")
            return redirect("draftBooks") # Redirect to prevent form resubmission

    # --- HANDLE PAGINATION ---
    paginator = Paginator(books_queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'books': page_obj,
        'search': search_query,
    }

    return render(request, 'my_books.html', context)

def publishedBooks(request):
    # We explicitly exclude drafts to be safe
    books_list = Book.objects.filter(
        uploaded_by=request.user, 
        is_published=True
    ).order_by('-uploaded_at')

    paginator = Paginator(books_list, 28)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    return render(request, 'published_books.html', {'books': books})



@login_required(login_url="/")
def my_community_posts(request):
    # 1. Subquery to check if current user liked the post 
    is_liked_subquery = Post.likes.through.objects.filter(
        post_id=OuterRef('pk'), 
        user_id=request.user.id
    )

    user_posts = Post.objects.filter(author=request.user)\
        .select_related('author', 'book')\
        .prefetch_related('images')\
        .annotate(
            has_liked=Exists(is_liked_subquery) 
        )\
        .order_by('-created_at')

    # 3. Pagination
    paginator = Paginator(user_posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'my_posts.html', {'posts': page_obj})