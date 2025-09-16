from django.shortcuts import render,get_object_or_404,redirect
from books.models import *
from .forms import BookContentForm
# Create your views here.

def dashboard(request):
    books = Book.objects.all().order_by("-uploaded_at")
    context = {"books":books}
    return render(request, 'dashboard.html',context)


def updateBook(request, slug):
    book = get_object_or_404(Book, slug=slug)
    bookcontent, created = BookContent.objects.get_or_create(book=book)

    if request.method == "POST":
        form = BookContentForm(request.POST, request.FILES, instance=bookcontent)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = BookContentForm(instance=bookcontent)

    return render(request, 'updateBook.html', {'book': book, 'form': form})
 
def addBook(request):
    return render(request, 'addbook.html')