from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from books.models import Genre, Book
from home.models import Notification
from django.core.cache import cache
import random
from django.db.models import F, ExpressionWrapper, FloatField, Func
from django.db.models.functions import Now, ExtractDay
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Feedback

def home(request):
    # 1. Categories
    categories = cache.get("home_categories")
    if categories is None:
        categories = list(Genre.objects.only("id", "name", "slug", "lucidicon"))
        cache.set("home_categories", categories, timeout=60 * 60 * 24)
    
    categories = categories[:]
    random.shuffle(categories)

    # 2. TRENDING ALGORITHM (Static Fields + Gravity)
    books = cache.get("home_books_trending")

    if books is None:
        books = list(
            Book.objects.filter(is_published=True)
            .select_related("genre")
            .defer("pdf_file", "audio_file", "price", "isbn", "updated_at")
            .annotate(
                # Calculate "Engagement Score" 
                # We give high weight to Likes/Saves, low weight to Views
                engagement=ExpressionWrapper(
                    (F('likes_count') * 5) + 
                    (F('read_later_count') * 3) + 
                    (F('views_count') * 1),
                    output_field=FloatField()
                ),
                
                # Calculate "Age" in days (handling NULLs/New uploads)
                # We add +2 to age so brand new books don't divide by zero
                book_age=ExpressionWrapper(
                    ExtractDay(Now() - F('uploaded_at')) + 2.0,
                    output_field=FloatField()
                )
            )
            .annotate(
                # Apply Gravity
                # Score = Engagement / Age^1.5
                # The power (1.5) determines how fast books "fall" off the trending list.
                # Higher number = Faster turnover (Fresh content wins).
                trending_score=ExpressionWrapper(
                    F('engagement') / Func(F('book_age'), 1.5, function='POWER'),
                    output_field=FloatField()
                )
            )
            .order_by('-trending_score')[:28]
        )

        cache.set("home_books_trending", books, timeout=60 * 15)

    return render(request, "home.html", {"books": books, "category": categories})

def aboutUs(request):
    return render(request, "aboutUs.html")

def promo_link(request,id):
    notif = Notification.objects.get(id=id)
    notif.is_read = True
    notif.save()
    if notif.promotional_link:
        return redirect(notif.promotional_link)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def submit_feedback(request):
    try:
        data = json.loads(request.body)
        feedback_type = data.get('feedback_type', 'Other')
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty.'}, status=400)
        
        # Check if the user is authenticated
        if request.user.is_authenticated:
            user_val = request.user.username 
        else:
            user_val = "unknown"

        # Create and save the feedback to the database
        Feedback.objects.create(
            user=user_val,
            feedback_type=feedback_type,
            message=message
        )

        return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again later.'}, status=500)

def customLogout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")