from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.utils.timesince import timesince
from django.template.defaultfilters import truncatechars
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from .models import Post, PostImage, Comment
from books.models import ReadBy, Book

# -------------------------------------------------------------------------
# 1. COMMUNITY FEED
# -------------------------------------------------------------------------
def community(request):
    page_number = request.GET.get('page', '1')
    feed_cache_key = f"community_feed:page:{page_number}"
    
    cached_data = cache.get(feed_cache_key)

    if cached_data is None:
        # --- DB QUERY ---
        posts_qs = (
            Post.objects
            .select_related('author', 'book')
            .prefetch_related('images')
            .order_by('-created_at')
        )

        paginator = Paginator(posts_qs, 20)
        page = paginator.get_page(page_number)

        # Force evaluation for caching
        posts_list = list(page.object_list)
        
        cached_data = {
            'posts': posts_list,
            'has_next': page.has_next(),
            'next_page_number': page.next_page_number() if page.has_next() else None,
        }
        cache.set(feed_cache_key, cached_data, 900)

    # Unpack
    posts = cached_data['posts']
    has_next = cached_data['has_next']
    next_page_number = cached_data['next_page_number']

    # 2. PERSONALIZATION (Is Liked?)
    if request.user.is_authenticated:
        liked_post_ids = set(
            Post.likes.through.objects.filter(
                user_id=request.user.id,
                post_id__in=[p.id for p in posts]
            ).values_list('post_id', flat=True)
        )

        for post in posts:
            post.has_liked = post.id in liked_post_ids

    # 3. SIDEBAR
    books = []
    if request.user.is_authenticated:
        sidebar_key = f"user_sidebar:{request.user.id}"
        books = cache.get(sidebar_key)

        if books is None:
            books = list(
                ReadBy.objects.filter(user=request.user)
                .select_related('book')[:5]
            )
            cache.set(sidebar_key, books, 1800)

    # 4. POST SUBMISSION
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        book_slug = request.POST.get("book", "").strip()
        image_file = request.FILES.get("image")

        if not content and not book_slug and not image_file:
            messages.error(request, "Cannot create an empty post.")
            return redirect("community")

        book_obj = None
        if book_slug:
            book_obj = Book.objects.filter(slug=book_slug).first()

        post = Post.objects.create(
            author=request.user,
            content=content,
            book=book_obj
        )

        if image_file:
            PostImage.objects.create(post=post, image=image_file)

        # Invalidate Cache
        try:
            cache.delete_pattern("community_feed:page:*")
        except AttributeError:
            cache.clear()

        messages.success(request, "Your post has been published!")
        return redirect("community")

    context = {
        "posts": posts,
        "books": books,
        "has_next": has_next, 
        "next_page_number": next_page_number,
    }
    return render(request, "community.html", context)


# -------------------------------------------------------------------------
# 2. SINGLE POST VIEW
# -------------------------------------------------------------------------
def viewPost(request, slug):
    queryset = Post.objects.select_related('author', 'book').prefetch_related('images')
    post = get_object_or_404(queryset, slug=slug)

    if request.user.is_authenticated:
        post.has_liked = post.likes.filter(id=request.user.id).exists()
        
        post_type = ContentType.objects.get_for_model(Post)
        request.user.notifications.filter(
            content_type=post_type,
            object_id=post.id, 
            is_read=False
        ).update(is_read=True)

    return render(request, 'viewpost.html', {'post': post})


# -------------------------------------------------------------------------
# 3. LIKE POST
# -------------------------------------------------------------------------
@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True

    # Signal updates the count, but we must refresh to see it in this request
    post.refresh_from_db()

    return JsonResponse({
        'likes_count': post.likes_count, 
        'is_liked': is_liked
    })


# -------------------------------------------------------------------------
# 4. DELETE POST
# -------------------------------------------------------------------------
@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return JsonResponse({
            'status': 'error', 
            'message': 'You are not authorized to delete this post.'
        }, status=403)

    post.delete()
    
    # Invalidate Cache
    try:
        cache.delete_pattern("community_feed:page:*")
    except AttributeError:
        cache.clear()

    return JsonResponse({
        'status': 'success', 
        'message': 'Post has been deleted successfully.' 
    })


# -------------------------------------------------------------------------
# 5. COMMENTS
# -------------------------------------------------------------------------
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
    
    # Signal updates comments_count automatically

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

    post_data = {
        "author": post.author.get_full_name(),
        "username": post.author.username,
        "avatar": f"https://i.pravatar.cc/150?u={post.author.username}",
        "content": truncatechars(post.content, 100),
        "created": timesince(post.created_at)
    }

    comments_data = [
        {
            "id":c.id,
            "author": c.author.get_full_name(),
            "username": c.author.username,
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



@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author == request.user or request.user.is_superuser:
        post = comment.post 
        comment.delete()
        
        post.comments_count = post.comments.count()
        post.save()

        return JsonResponse({'status': 'success', 'message': 'Comment deleted successfully'})
    
    else:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)