from django.shortcuts import render, get_object_or_404, redirect
from books.models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import BookContentForm,BookForm
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
    books_list = Book.objects.select_related("genre").filter(uploaded_by=request.user).order_by("-uploaded_at")

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
    # Fetch objects
    book = get_object_or_404(Book, slug=slug, uploaded_by=request.user)
    bookcontent, created = BookContent.objects.get_or_create(book=book)

    # Initialize forms with instances
    if request.method == "POST":
        book_form = BookForm(request.POST, request.FILES, instance=book)
        content_form = BookContentForm(request.POST, request.FILES, instance=bookcontent)

        if book_form.is_valid() and content_form.is_valid():
            # OPTIMIZED BOOK SAVE
            if book_form.has_changed():
                # Attach user for signals/tracking
                book = book_form.save(commit=False)
                book._updated_by = request.user
                
                # Only update specific fields that changed in the DB
                book.save(update_fields=book_form.changed_data) 
            
            # CONTENT SAVE
            if content_form.has_changed():
                content = content_form.save(commit=False)
                content._updated_by = request.user

                content.save(update_fields=content_form.changed_data)

            # Handle redirection
            action = request.POST.get("action")
            if action == "save":
                return redirect("dashboard")
            elif action == "continue":
                return redirect("updateBook", slug=book.slug)

    else:
        book_form = BookForm(instance=book)
        content_form = BookContentForm(instance=bookcontent)

    context = {
        "book_form": book_form,
        "content_form": content_form,
        "book": book,
    }

    return render(request, "updateBook.html", context)



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
                uploaded_by=request.user
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
    book = get_object_or_404(Book.objects.select_related("genre"), slug=slug, uploaded_by=request.user)
    bookcontent = get_object_or_404(BookContent.objects.only("content"), book=book)
    return render(
        request, "viewBook.html", {"book": book, "bookcontent": bookcontent.content}
    )
