from django.urls import path, include
from home import views


urlpatterns = [
    path('', views.home, name='home'),
    path('book/', include('books.urls')),
    path('admin-dashboard/', include('LRAdmin.urls')),

]
