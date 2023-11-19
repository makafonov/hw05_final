from django.urls import path

from apps.posts.views.comments import AddCommentView
from apps.posts.views.follow import (
    FollowIndexView,
    ProfileFollowView,
    ProfileUnfollowView,
)
from apps.posts.views.groups import GroupView
from apps.posts.views.posts import (
    IndexListView,
    NewPostCreateView,
    PostDetailView,
    PostEditView,
)
from apps.posts.views.profile import ProfileView


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
