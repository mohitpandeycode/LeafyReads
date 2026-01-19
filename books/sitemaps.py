from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from books.models import Book 

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'  # Force HTTPS links

    def items(self):
        return ['home', 'aboutUs'] 

    def location(self, item):
        return reverse(item)

class BookSitemap(Sitemap):
    """
    Handles the dynamic Book pages.
    """
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Book.objects.filter(is_published=True).only('id', 'slug', 'updated_at')

    def lastmod(self, obj):
        return obj.updated_at
        