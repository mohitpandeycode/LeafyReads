from django.shortcuts import render, get_object_or_404, redirect
from books.models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import BookContentForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from books.models import Book

# Create your views here.


def loginAdmin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(
                request,
                f'An admin account with the username "{username}" was not found.',
            )
            return redirect("login_admin")

        if not user.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("login_admin")

        if not user.is_staff:
            messages.error(request, "This account does not have admin privileges.")
            return redirect("login_admin")

        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        return redirect("dashboard")

    return render(request, "loginAdmin.html")


@login_required(login_url="login_admin")
def dashboard(request):

    if request.method == "POST":
        action = request.POST.get("action")
        selected_books = request.POST.getlist("selected_books")
        
        if action == "delete" and selected_books:
            # Perform delete operation
            for book in Book.objects.filter(id__in=selected_books):
                book._updated_by = request.user
                book.delete()
            return redirect("dashboard")


    
    # Start with all books, fetch genre relationship efficiently
    books_list = Book.objects.select_related("genre").all().order_by("-uploaded_at")

    book_query = request.GET.get("search", "").strip()

    if book_query:
        
        keywords = book_query.split()
        query = Q()
        for keyword in keywords:
            q = (
                Q(title__icontains=keyword)
                | Q(author__icontains=keyword)
                | Q(genre__name__icontains=keyword)
                | Q(slug__icontains=keyword)
            )
            query |= q
            
        books_list = books_list.filter(query).distinct()
        
    #Apply Pagination 

    PAGESIZE = 50
    paginator = Paginator(books_list, PAGESIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "books": page_obj,
        "search": book_query,
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="login_admin")
def updateBook(request, slug):
    book = get_object_or_404(Book, slug=slug)
    bookcontent, created = BookContent.objects.get_or_create(book=book)
    genres = Genre.objects.all()

    if request.method == "POST":
        form = BookContentForm(request.POST, request.FILES, instance=bookcontent)
        if form.is_valid():
            # Attach user to both book and bookcontent before saving
            book._updated_by = request.user
            bookcontent._updated_by = request.user

            # Save book content (triggers content_update signal)
            form.save()

            # Update book fields
            book.title = request.POST.get("title")
            book.slug = request.POST.get("slug")
            book.author = request.POST.get("author")
            book.price = request.POST.get("price") or None
            book.isbn = request.POST.get("isbn") or None
            book.is_published = "is_published" in request.POST

            genre_id = request.POST.get("genre")
            book.genre = Genre.objects.get(id=genre_id) if genre_id else None

            if "cover_front" in request.FILES:
                book.cover_front = request.FILES["cover_front"]
            if "audio_file" in request.FILES:
                book.audio_file = request.FILES["audio_file"]

            # Save book (triggers update signal)
            book.save()

            action = request.POST.get("action")
            if action == "save":
                return redirect("dashboard")
            elif action == "continue":
                return redirect("updateBook", slug=book.slug)
    else:
        form = BookContentForm(instance=bookcontent)

    return render(
        request,
        "updateBook.html",
        {"book": book, "form": form, "genres": genres},
    )



@login_required(login_url="login_admin")
def addBook(request):
    genres = Genre.objects.all()

    if request.method == "POST":
        form = BookContentForm(request.POST, request.FILES)
        if form.is_valid():
            book = Book(
                title=request.POST.get("title"),
                slug=request.POST.get("slug"),
                author=request.POST.get("author"),
                price=request.POST.get("price") or None,
                isbn=request.POST.get("isbn") or None,
                is_published="is_published" in request.POST,
                genre=Genre.objects.get(id=request.POST.get("genre")) if request.POST.get("genre") else None,
                cover_front=request.FILES.get("cover_front"),
                audio_file=request.FILES.get("audio_file"),
            )
            book._updated_by = request.user  # <-- attach user
            book.save()  # triggers Book "create" log

            # Save book content
            bookcontent = form.save(commit=False)
            bookcontent.book = book
            bookcontent.book._updated_by = request.user  # attach for content log
            bookcontent.save()  # triggers BookContent "create" log

            action = request.POST.get("action")
            if action == "save":
                return redirect("dashboard") 
            elif action == "add_another":
                return redirect("addBook")
            elif action == "continue":
                return redirect("updateBook", slug=book.slug)
    else:
        form = BookContentForm()

    return render(request, "addbook.html", {"form": form, "genres": genres})


@login_required(login_url="login_admin")
def viewBookAdmin(request, slug):
    book = get_object_or_404(Book.objects.select_related("genre"), slug=slug)
    bookcontent = get_object_or_404(BookContent.objects.only("content"), book=book)
    return render(
        request, "viewBook.html", {"book": book, "bookcontent": bookcontent.content}
    )
