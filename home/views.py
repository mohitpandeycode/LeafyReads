from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from books.models import *
from django.db.models import Count
from django.core.cache import cache
from django.db import connection

def home(request):
    categories = cache.get("home_categories") 
    if categories is None:
        categories = list(
                Genre.objects.only("id", "name", "slug", "lucidicon").order_by("pk")
            )
        cache.set("home_categories", categories, timeout=60 * 60 * 24)

    # Fetch Books (Cache for 15 minutes) ---
    books = cache.get("home_books")
    
    if books is None:
        books = list(
            Book.objects.select_related("genre")
            .annotate(likes_count=Count("likes"))
            .annotate(readby_count=Count("readbooks"))
            .defer("pdf_file", "audio_file", "price", "isbn", "updated_at")
            .order_by("-uploaded_at")[:12]
        )
        cache.set("home_books", books, timeout=60 * 15)

    return render(request, "home.html", {"books": books, "category": categories})


def aboutUs(request):
    return render(request, "aboutUs.html")


def customLogout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")
