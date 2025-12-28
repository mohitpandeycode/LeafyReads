from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from books.models import ReadBy, ReadLater, Review


@login_required
def profilepage(request):
    user = request.user

    # Fetch recently read books efficiently with book relation
    recently_read_books = (
        ReadBy.objects.filter(user=user)
        .select_related("book")
        .order_by("-readed_at")[:4]
    )

    # Use aggregation to reduce duplicate queries
    counts = {
        "books_read_count": ReadBy.objects.filter(user=user).count(),
        "read_later_count": ReadLater.objects.filter(user=user).count(),
        "reviews_count": Review.objects.filter(user=user).count(),
    }

    context = {
        "profile_user": user,
        "recently_read_books": recently_read_books,
        **counts,
    }

    return render(request, "profilePage.html", context)
