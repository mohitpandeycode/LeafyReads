from django.urls import path
from userSection import views


urlpatterns = [
    path('', views.profilepage, name='profilepage'),
    path('create-new-book/', views.createBook, name='createBook'),
    path('update-book/<slug:slug>/', views.updateUserBook, name='updateUserBook'),
    path('uploaded-books/', views.draftBooks, name='draftBooks'),
    path('published-books/', views.publishedBooks, name='publishedBooks'),
    path('read-books/', views.readBooks, name='readBooks'),
    path('my-posts/', views.my_community_posts, name='my_community_posts'),


]