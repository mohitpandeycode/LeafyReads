from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Post, PostImage,Comment
from books.models import ReadBy, Book
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from django.utils.timesince import timesince
from django.template.defaultfilters import truncatechars


def community(request):
    # Fetch posts with calculated counts instead of loading objects
    posts_qs = Post.objects.select_related('author', 'book').annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    ).order_by('-created_at')

    if request.user.is_authenticated:
        is_liked = Post.likes.through.objects.filter(
            post_id=OuterRef('pk'),
            user_id=request.user.id
        )
        posts_qs = posts_qs.annotate(has_liked=Exists(is_liked))

    # Prefetch images
    posts_qs = posts_qs.prefetch_related('images')

    # Only fetch 10 posts at a time to keep the page fast
    paginator = Paginator(posts_qs, 20) 
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    # Optimized watched book query
    books =[]
    if request.user.is_authenticated:
        books = ReadBy.objects.filter(user=request.user).select_related('book')[:5]

    # POST SUBMISSION LOGIC ---
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        book_slug = request.POST.get("book", "").strip()
        image_file = request.FILES.get("image", None)

        if not content and not book_slug and not image_file:
            messages.error(request, "Cannot create an empty post.")
            return redirect("community")

        book_obj = None
        if book_slug:
            book_obj = Book.objects.filter(slug=book_slug).first()

        # Create Post
        post = Post.objects.create(
            author=request.user,
            content=content,
            book=book_obj
        )

        # Handle Image
        if image_file:
            PostImage.objects.create(post=post, image=image_file)

        messages.success(request, "Your post has been created!")
        return redirect("community")

    context = {
        "posts": posts_page,
        "books": books,
    }
    return render(request, "community.html", context)



@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    
    # Toggle Like Logic
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True

    return JsonResponse({
        'likes_count': post.likes.count(),
        'is_liked': is_liked
    })
    
    
@login_required
@require_POST
def add_comment(request):
    post_id = request.POST.get("post_id")
    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"error": "Empty comment"}, status=400)

    post = get_object_or_404(Post, id=post_id)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content
    )

    return JsonResponse({
        "id": comment.id,
        "author": comment.author.get_full_name(),
        "content": comment.content,
        "created": "Just now"
    })
    
    
@require_GET
def get_comments(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    comments = post.comments.select_related("author").order_by("created_at")

    #Prepare Post Data separately
    post_data = {
        "author": post.author.get_full_name(),
        "username": post.author.username,
        "avatar": f"https://i.pravatar.cc/150?u={post.author.username}",
        "content": truncatechars(post.content, 100),
        "created": timesince(post.created_at)
    }

    #Prepare Comment List
    comments_data = [
        {
            "author": c.author.get_full_name(),
            "avatar": f"https://i.pravatar.cc/54?u={c.author.username}",
            "content": c.content,
            "created": c.created_at.strftime("%b %d, %H:%M"),
        }
        for c in comments
    ]

    return JsonResponse({
        "post": post_data, 
        "comments": comments_data
    })