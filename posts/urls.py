from django.urls import path

from posts.views.comments import AddCommentView
from posts.views.follow import (
    FollowIndexView,
    ProfileFollowView,
    ProfileUnfollowView,
)
from posts.views.groups import GroupView
from posts.views.posts import (
    IndexListView,
    NewPostCreateView,
    PostDetailView,
    PostEditView,
)
from posts.views.profile import ProfileView


app_name = 'posts'

urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('new/', NewPostCreateView.as_view(), name='new_post'),
    path('follow/', FollowIndexView.as_view(), name='follow_index'),
    path('group/<slug:slug>/', GroupView.as_view(), name='group'),
    path('<str:username>/', ProfileView.as_view(), name='profile'),
    path(
        '<str:username>/<int:pk>/',
        PostDetailView.as_view(),
        name='post',
    ),
    path(
        '<str:username>/<int:pk>/edit/',
        PostEditView.as_view(),
        name='post_edit',
    ),
    path(
        '<str:username>/<int:pk>/comment/',
        AddCommentView.as_view(),
        name='add_comment',
    ),
    path(
        '<str:username>/follow/',
        ProfileFollowView.as_view(),
        name='profile_follow',
    ),
    path(
        '<str:username>/unfollow/',
        ProfileUnfollowView.as_view(),
        name='profile_unfollow',
    ),
]
