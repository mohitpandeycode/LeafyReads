from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.cache import cache
from .models import Post, PostImage, Comment
import base64
import uuid
from bs4 import BeautifulSoup
from books.models import ReadBy



def community(request):
    # --- HANDLE POST REQUEST (Create Post) ---
    if request.method == "POST":
        raw_content = request.POST.get("content")

        if not raw_content or not raw_content.strip():
            return redirect("community")

        post = Post.objects.create(author=request.user, content="Processing...")

        # image processing logic
        soup = BeautifulSoup(raw_content, "html.parser")
        for button in soup.find_all("button", class_="remove-image-btn-frontend"):
            button.decompose()
        images = soup.find_all("img")
        for img_tag in images:
            if img_tag.get("src", "").startswith("data:image"):
                try:
                    header, data = img_tag["src"].split(";base64,")
                except ValueError: continue
                try:
                    decoded_file = base64.b64decode(data)
                except (TypeError, ValueError): continue

                file_extension = header.split("/")[-1]
                file_name = f"{uuid.uuid4()}.{file_extension}"
                django_file = ContentFile(decoded_file, name=file_name)

                post_image = PostImage.objects.create(post=post, image=django_file)
                img_tag["src"] = post_image.image.url

        post.content = str(soup)
        post.save()
        cache.delete("community_posts_list")
        return redirect("community")

    # --- HANDLE GET REQUEST

    #Fetch Global Posts (Cached)
    posts = cache.get("community_posts_list")
    
    if posts is None:
        # Cache MISS: Run the heavy database query
        posts = list(
            Post.objects.select_related("author", "book")
            .prefetch_related("likes", "comments", "images")
            .order_by("-created_at")
            .all()
        )
        # Store in cache for 5 minutes (300 seconds)
        cache.set("community_posts_list", posts, timeout=300)

    # Fetch User-Specific Books (Cached per User)
    books = None
    if request.user.is_authenticated:
        # Unique cache key for this specific user
        user_books_key = f"community_readby_{request.user.id}"
        books = cache.get(user_books_key)
        
        if books is None:
            books = list(
                ReadBy.objects.filter(user=request.user)
                .select_related("book")
                .order_by("-readed_at")[:5]
            )
            cache.set(user_books_key, books, timeout=60 * 10)
    else:
        books = {"no books": "no books"}

    context = {"posts": posts, "books": books}

    return render(request, "community.html", context)