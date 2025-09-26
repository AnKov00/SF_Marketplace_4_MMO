from django.urls import path
from .views import (PostView, PostDetailView, CreateResponse, CreatePostView,
                    MyPostList, PostEdit)


urlpatterns = [
    path('', PostView.as_view(), name='post_list'),
    path('my-posts', MyPostList.as_view(), name='my_posts'),
    path('post/create/', CreatePostView.as_view(), name='create_post'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/response/', CreateResponse.as_view(), name='add_response'),
    path('post/<slug:slug>/edit', PostEdit.as_view(), name='edit_post'),
]
