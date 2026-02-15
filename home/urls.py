from django.urls import path, include
from home import views



urlpatterns = [
    path('', views.home, name='home'),
    path('aboutus/', views.aboutUs, name = "aboutUs"),
    path('admin-dashboard/', include('LRAdmin.urls')),
    path('logout/', views.customLogout, name='logout'),
    path('redirecting/<id>',views.promo_link, name="promo_link")

]
