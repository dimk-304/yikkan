from django.urls import path
from . import views

app_name = 'networking'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('post/create/', views.create_post, name='create'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete'),
]
