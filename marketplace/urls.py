from django.urls import path
from .views import PostView, PostDetailView, CreateResponse


urlpatterns = [
    path('', PostView.as_view(), name='post_list'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/response/', CreateResponse.as_view(), name='add_response'),
]
