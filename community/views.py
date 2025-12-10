from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, PostImage, Comment
from books.models import ReadBy, Book
from django.contrib import messages


def community(request):
    # Prefetch related data for efficiency
    posts = (
        Post.objects.all()
        .select_related('author', 'book')
        .prefetch_related('images', 'likes', 'comments')
    )
    
    books = ReadBy.objects.filter(user=request.user)  # Recent read books

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        book_slug = request.POST.get("book", "").strip()
        image_file = request.FILES.get("image", None)

        # Validate: At least caption, book mention, or image must exist
        if not content and not book_slug and not image_file:
            messages.error(request, "Cannot create an empty post. Add text, a book mention, or an image.")
            return redirect("community")

        # Resolve Book object safely
        book_obj = None
        if book_slug:
            book_obj = Book.objects.filter(slug=book_slug).first()

        # Create the Post
        post = Post.objects.create(
            author=request.user,
            content=content,
            book=book_obj
        )

        # Attach image if uploaded
        if image_file:
            PostImage.objects.create(post=post, image=image_file)

        messages.success(request, "Your post has been created!")
        return redirect("community")

    context = {
        "posts": posts,
        "books": books,
    }
    return render(request, "community.html", context)