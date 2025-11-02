from django.urls import path
from books import views


urlpatterns = [
    path('library/open/<slug>', views.home, name='book'),
    path('category/<slug:slug>/', views.categories, name='category'),
    path('library/', views.library, name='library'),
    path('my-books/', views.myBooks, name='myBooks'),
    path('search-results-of/', views.searchbooks, name='searchbooks'),
    path('ajax/search/', views.ajax_search, name='ajax_search'),
    path('toggle-read-later/<slug:book_slug>/', views.toggle_read_later, name='toggle_read_later'),
    path('toggle-like/<slug:book_slug>/', views.toggle_like, name='toggle_like'),

    

]
