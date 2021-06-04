from django.urls import path

from posts import views


urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('new/', views.NewPostCreateView.as_view(), name='new_post'),
    path('follow/', views.FollowIndexView.as_view(), name='follow_index'),
    path('group/<slug:slug>/', views.GroupView.as_view(), name='group'),
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),
    path(
        '<str:username>/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post',
    ),
    path(
        '<str:username>/<int:pk>/edit/',
        views.PostEditView.as_view(),
        name='post_edit',
    ),
    path(
        '<str:username>/<int:pk>/comment/',
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
