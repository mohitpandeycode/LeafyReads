
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from books.sitemaps import StaticViewSitemap, BookSitemap 

sitemaps = {
    'static': StaticViewSitemap,
    'books': BookSitemap,
}



urlpatterns = [
    path('tryhardadmin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('', include('home.urls')),
    path('profile/', include('userSection.urls')),
    path('book/', include('books.urls')),
    path('community/', include('community.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('ht/', include('health_check.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
