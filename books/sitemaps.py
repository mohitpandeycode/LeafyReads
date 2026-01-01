from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from books.models import Book 

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

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

    def items(self):
        # OPTIMIZATION: .only() fetches ONLY these fields from the DB.
        return Book.objects.only('id', 'title', 'uploaded_at','author','updated_at','slug').all()

    def lastmod(self, obj):
        return obj.updated_at