from django.urls import path
from LRAdmin import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.loginAdmin, name='login_admin'),
    path('add-book/', views.addBook, name='addBook'),
    path('user-uploads-books/', views.userUploads, name='userUploads'),
    path('updated-book/<slug:slug>/', views.updateBook, name='updateBook'),
    path('viewBook-Admin/<slug:slug>/', views.viewBookAdmin, name='viewBookAdmin'),

]