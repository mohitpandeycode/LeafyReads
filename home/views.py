from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from books.models import *
from django.db.models import Count
from django.views.decorators.cache import cache_page
from django.db import connection
import time


def home(request):
    categories = Genre.objects.only("id", "name", "slug", "lucidicon").order_by("pk")
    books = (
        Book.objects.select_related("genre")
        .annotate(likes_count=Count("likes"))
        .annotate(readby_count=Count("readbooks"))
        .defer("pdf_file", "audio_file", "price", "isbn", "updated_at")
        .order_by("-uploaded_at")[:12]
    )
    return render(request, "home.html", {"books": books, "category": categories})


def aboutUs(request):
    return render(request, "aboutUs.html")


def customLogout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")
