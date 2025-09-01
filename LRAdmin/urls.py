from django.urls import path
from LRAdmin import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-book', views.addBook, name='addBook'),

]