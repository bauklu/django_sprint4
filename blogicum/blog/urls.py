from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category>/', views.category_posts,
         name='category_posts'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<slug:username>/', views.ProfileView.as_view(),
         name='profile'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<post_id>/edit/', views.edit_post,
         name='edit_post'),
    path('posts/<post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<post_id>/edit_comment/<comment_id>/', views.edit_comment,
         name='edit_comment'),
    path('posts/<post_id>/delete_comment/<comment_id>/',
         views.delete_comment, name='delete_comment'),
]
