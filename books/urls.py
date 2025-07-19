from django.urls import path
from books import views


urlpatterns = [
    path('book/<slug>', views.home, name='book'),
    path('category/<slug:slug>/', views.categories, name='category'),
    path('library/', views.library, name='library'),
    path('your-saved-books/', views.myBooks, name='myBooks'),
    path('search-results-of/', views.searchbooks, name='searchbooks'),

]
