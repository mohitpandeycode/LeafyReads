from django.urls import path
from community import views

urlpatterns = [
    path('',views.community,name = "community"),
    path('post-view/<slug:slug>/', views.viewPost, name="post_view"),
    path('ajax/like/', views.like_post, name='like_post'),
    path("comment/add/", views.add_comment, name="add_comment"),
    path("comment/<int:post_id>/", views.get_comments, name="get_comments"),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),

]
