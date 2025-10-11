from django.urls import path, include
from home import views


urlpatterns = [
    path('', views.home, name='home'),
    path('book/', include('books.urls')),
    path('aboutus/', views.aboutUs, name = "aboutUs"),
    path('ourcommunity/', views.community, name = "community"),
    path('admin-dashboard/', include('LRAdmin.urls')),
    path('profile/', include('userSection.urls')),
    path('logout/', views.customLogout, name='logout'),

]
