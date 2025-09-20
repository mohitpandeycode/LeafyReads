from django.shortcuts import render,get_object_or_404,redirect
from books.models import *
from .forms import BookContentForm
from django.db.models import Q
# Create your views here.

def dashboard(request):
    books = Book.objects.all().order_by("-uploaded_at")
    if request.method == "POST":
        action = request.POST.get('action')
        selected_books = request.POST.getlist('selected_books')
        if action == 'delete' and selected_books:
            Book.objects.filter(id__in=selected_books).delete()
        return redirect('dashboard')  # refresh page after action

    book_query = request.GET.get('search', '').strip()
    books = Book.objects.select_related('genre').all().order_by('-uploaded_at')

    if book_query:
        keywords = book_query.split()
        query = Q()
        for keyword in keywords:
            q = (
                Q(title__icontains=keyword) |
                Q(author__icontains=keyword) |
                Q(genre__name__icontains=keyword) |
                Q(slug__icontains=keyword)
            )
            query |= q
        books = books.filter(query).distinct()
    context = {"books": books}
    return render(request, 'dashboard.html', context)


def updateBook(request, slug):
    book = get_object_or_404(Book, slug=slug)
    bookcontent, created = BookContent.objects.get_or_create(book=book)

    genres = Genre.objects.all()

    if request.method == "POST":
        form = BookContentForm(request.POST, request.FILES, instance=bookcontent)
        if form.is_valid():
            form.save()

            # Update Book fields
            book.title = request.POST.get("title")
            book.slug = request.POST.get("slug")
            book.author = request.POST.get("author")
            book.price = request.POST.get("price") or None
            book.isbn = request.POST.get("isbn") or None
            book.is_published = "is_published" in request.POST

            genre_id = request.POST.get("genre")
            book.genre = Genre.objects.get(id=genre_id) if genre_id else None

            # Files
            if "cover_front" in request.FILES:
                book.cover_front = request.FILES["cover_front"]
            if "audio_file" in request.FILES:
                book.audio_file = request.FILES["audio_file"]

            book.save()

            # Check which button was pressed
            action = request.POST.get("action")
            if action == "save":
                return redirect('dashboard')
            elif action == "continue":
                return redirect('updateBook', slug=book.slug)

    else:
        form = BookContentForm(instance=bookcontent)

    return render(
        request,
        "updateBook.html",
        {"book": book, "form": form, "genres": genres}
    )


def addBook(request):
    genres = Genre.objects.all()

    if request.method == "POST":
        form = BookContentForm(request.POST, request.FILES)
        if form.is_valid():
            # create Book first
            book = Book.objects.create(
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

            # save book content
            bookcontent = form.save(commit=False)
            bookcontent.book = book
            bookcontent.save()

            action = request.POST.get("action")
            if action == "save":
                return redirect("dashboard")  # back to list
            elif action == "add_another":
                return redirect("addBook")  # clear form for another
            elif action == "continue":
                return redirect("updateBook", slug=book.slug)  # go into editing mode

    else:
        form = BookContentForm()

    return render(request, "addbook.html", {"form": form, "genres": genres})


def viewBookAdmin(request, slug):
    book = get_object_or_404(Book.objects.select_related('genre'), slug=slug)
    bookcontent = get_object_or_404(BookContent.objects.only('content'), book=book)
    return render(request, 'viewBook.html', {'book': book, 'bookcontent': bookcontent.content})