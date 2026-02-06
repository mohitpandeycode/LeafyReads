from django.shortcuts import render, get_object_or_404, redirect
from books.models import *
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import BookContentForm,BookForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test

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
                f'We are unable to login you. Invalid Credential',
            )
            return redirect("login_admin")

        if not user.check_password(password):
            messages.error(request, "We are unable to login you. Invalid Credential.")
            return redirect("login_admin")

        if not user.is_staff:
            messages.error(request, "We are unable to login you. Invalid Credential.")
            return redirect("login_admin")

        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        return redirect("dashboard")

    return render(request, "loginAdmin.html")


@user_passes_test(lambda u: u.is_staff, login_url="login_admin")
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

    PAGESIZE = 20
    paginator = Paginator(books_list, PAGESIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "books": page_obj,
        "search": book_query,
    }
    return render(request, "dashboard.html", context)



@user_passes_test(lambda u: u.is_staff, login_url="login_admin")
def updateBook(request, slug):
    # Fetch objects
    book = get_object_or_404(Book, slug=slug)
    bookcontent, created = BookContent.objects.get_or_create(book=book)

    # Initialize forms
    if request.method == "POST":
        book_form = BookForm(request.POST, request.FILES, instance=book)
        content_form = BookContentForm(request.POST, request.FILES, instance=bookcontent)

        if book_form.is_valid() and content_form.is_valid():
            
            # --- 1. BOOK SAVE ---
            if book_form.has_changed():
                book = book_form.save(commit=False)
                book._updated_by = request.user
                # Optimization: This is safe for the Book model because 
                # we don't have custom 'save' logic that modifies other fields on the fly.
                book.save(update_fields=book_form.changed_data) 
            
            # --- 2. CONTENT SAVE---
            if content_form.has_changed():
                content = content_form.save(commit=False)
                content._updated_by = request.user
                content.save() 

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


@user_passes_test(lambda u: u.is_staff, login_url="login_admin")
def addBook(request):
    genres = Genre.objects.all()

    if request.method == "POST":
        # Initialize both forms
        book_form = BookForm(request.POST, request.FILES)
        content_form = BookContentForm(request.POST, request.FILES)

        if book_form.is_valid() and content_form.is_valid():
            
            # 1. Save Book
            book = book_form.save(commit=False)
            book.uploaded_by = request.user
            book._updated_by = request.user
            book.save()  # Full save triggers creation logs

            # 2. Save Content
            bookcontent = content_form.save(commit=False)
            bookcontent.book = book
            bookcontent.book._updated_by = request.user
            

            bookcontent.save() 

            # 3. Handle Actions
            action = request.POST.get("action")
            if action == "save":
                return redirect("dashboard") 
            elif action == "add_another":
                return redirect("addBook")
            elif action == "continue":
                return redirect("updateBook", slug=book.slug)
    else:
        book_form = BookForm()
        content_form = BookContentForm()

    return render(request, "addbook.html", {
        "book_form": book_form,  
        "content_form": content_form, 
        "genres": genres
    })


@user_passes_test(lambda u: u.is_staff, login_url="login_admin")
def viewBookAdmin(request, slug):
    book = get_object_or_404(Book.objects.select_related("genre"), slug=slug)
    bookcontent = get_object_or_404(BookContent.objects.only("content"), book=book)
    return render(
        request, "viewBook.html", {"book": book, "bookcontent": bookcontent.content}
    )


@user_passes_test(lambda u: u.is_staff, login_url="login_admin")
def userUploads(request):

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
    books_list = Book.objects.select_related("genre").filter(is_draft=False).order_by("-uploaded_at")

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
    return render(request, "userUploadsDashboard.html", context)
    