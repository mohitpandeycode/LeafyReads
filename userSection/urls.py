from django.urls import path,include
from userSection import views


urlpatterns = [
    path('', views.profilepage, name='profilepage'),
    path('book/', include('books.urls')),


]