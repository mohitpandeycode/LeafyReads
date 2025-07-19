from django.shortcuts import render, get_object_or_404,HttpResponse
from books.models import *
from django.db.models import Q


def home(request, slug):
    book = get_object_or_404(Book, slug=slug)
    bookcontent = get_object_or_404(BookContent,book=book)
    
    return render(request, 'book.html', {'book': book,'bookcontent':bookcontent.content})

def library(request):
    books = Book.objects.all().order_by('-uploaded_at')
    title =  "The books Library" 
    context = {
        'books': books,
        'title': title
    }
    return render(request,'library.html',context)

def categories(request, slug):
    category = get_object_or_404(Genre, slug = slug)
    books = Book.objects.filter(genre=category).order_by('-uploaded_at')
    title=category.name + " Books"
    context = {
        'books':books,
        'title': title,
        'category':f" of {category.name} Books"
    }
    return render(request, 'library.html',context)


def myBooks(request):
    books = ReadLater.objects.filter(user=request.user)
    context = {
        'books':books,
        'title': "Your Wishlist",
    }
    
    return render(request, 'library.html',context)



# Search books
def searchbooks(request):
    book_query = request.GET.get('search', '').strip()

    books = Book.objects.all().order_by('-uploaded_at')

    if book_query:
        # Split search query into individual keywords
        keywords = book_query.split()

        # Start an empty Q object
        query = Q()

        for keyword in keywords:
            query |= Q(title__icontains=keyword)
            query |= Q(author__icontains=keyword)
            query |= Q(genre__name__icontains=keyword)
            query |= Q(slug__icontains=keyword)

        books = books.filter(query).distinct()
    context =  {
                'books': books,
                'search': book_query,
                'title':"Search result of " + book_query + " Books",
                }
    return render(request, 'library.html',context)