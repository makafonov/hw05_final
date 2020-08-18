from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('404/', views.PageNotFoundView.as_view()),
    path('505/', views.server_error),
    path('new/', views.NewPostCreateView.as_view(), name='new_post'),
    path('follow/', views.FollowIndexView.as_view(), name='follow_index'),
    path('group/<slug:slug>/', views.GroupListView.as_view(), name='group'),
    path('<str:username>/', views.ProfileListView.as_view(), name='profile'),
    path(
        '<str:username>/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post',
    ),
    path(
        '<str:username>/<int:post_id>/edit/',
        views.PostEditView.as_view(),
        name='post_edit',
    ),
    path(
        '<str:username>/<int:post_id>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment',
    ),
    path(
        '<str:username>/follow/',
        views.ProfileFollowView.as_view(),
        name='profile_follow',
    ),
    path(
        '<str:username>/unfollow/',
        views.ProfileUnfollowView.as_view(),
        name='profile_unfollow',
    ),
]
