from django.urls import path
from userSection import views


urlpatterns = [
    path('', views.profilepage, name='profilepage'),


]