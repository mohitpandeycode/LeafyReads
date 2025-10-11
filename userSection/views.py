from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User  # Use the default User model
from books.models import Book, ReadBy, ReadLater, Review

@login_required
def profilepage(request):
    profile_user = request.user

    context = {
        'profile_user': profile_user,
        'books_read_count': ReadBy.objects.filter(user=profile_user).count(),
        'read_later_count': ReadLater.objects.filter(user=profile_user).count(),
        'reviews_count': Review.objects.filter(user=profile_user).count(),
    }
    return render(request, 'profilePage.html', context)

