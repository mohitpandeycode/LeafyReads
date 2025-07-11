from django.urls import path
from books import views


urlpatterns = [
    path('book/<slug>', views.home, name='book'),
    

]
