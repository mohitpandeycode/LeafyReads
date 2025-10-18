from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from .models import Post, PostImage, Comment
import base64
import uuid
from bs4 import BeautifulSoup 

@login_required
def community(request):

    if request.method == 'POST':
        raw_content = request.POST.get('content')

        if not raw_content or not raw_content.strip():
            return redirect('community')

        post = Post.objects.create(author=request.user, content="Processing...")

        soup = BeautifulSoup(raw_content, 'html.parser')

        # --- FIX: Find and remove the frontend-only remove buttons ---
        # This cleans the HTML before it's processed and saved.
        for button in soup.find_all('button', class_='remove-image-btn-frontend'):
            button.decompose()

        images = soup.find_all('img')

        for img_tag in images:
            if img_tag.get('src', '').startswith('data:image'):
                try:
                    header, data = img_tag['src'].split(';base64,')
                except ValueError:
                    continue
                
                try:
                    decoded_file = base64.b64decode(data)
                except (TypeError, ValueError):
                    continue

                file_extension = header.split('/')[-1]
                file_name = f"{uuid.uuid4()}.{file_extension}"
                django_file = ContentFile(decoded_file, name=file_name)

                post_image = PostImage.objects.create(post=post, image=django_file)
                img_tag['src'] = post_image.image.url
        
        post.content = str(soup)
        post.save()
        
        return redirect('community')

    # Fetch posts and their related data
    posts = Post.objects.select_related(
        'author', 
        'book'
    ).prefetch_related(
        'likes', 
        'comments',
        'images'
    ).all()
    
    context = {
        'posts': posts
    }
    
    return render(request, 'community.html', context)

