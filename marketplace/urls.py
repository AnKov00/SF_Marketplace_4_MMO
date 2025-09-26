from django.urls import path
from .views import (PostView, PostDetailView, CreateResponse, CreatePostView,
                    MyPostList, PostEdit, DeleteMediaView, ResponseListView,
                    ResponseUpdateView, ResponseDeleteView)


urlpatterns = [
    path('', PostView.as_view(), name='post_list'),
    path('my-posts', MyPostList.as_view(), name='my_posts'),
    path('post/create/', CreatePostView.as_view(), name='create_post'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/response/', CreateResponse.as_view(), name='add_response'),
    path('post/<slug:slug>/edit', PostEdit.as_view(), name='edit_post'),
    path('media/<int:int>/delete/', DeleteMediaView.as_view(), name='delete_media'),
    path('my-responses/', ResponseListView.as_view(), name='response_list'),
    path('response/<int:pk>/update/', ResponseUpdateView.as_view(), name='response_update'),
    path('response/<int:pk>/delete/', ResponseDeleteView.as_view(), name='response_delete'),
]
