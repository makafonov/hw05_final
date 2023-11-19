from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from apps.posts.mixins import PytestGetMixin, PytestMixin, SameUserFollowMixin
from apps.posts.models import Follow, Post, User


class FollowIndexView(LoginRequiredMixin, PytestMixin, ListView):
    """Избранные авторы. Главная страница."""

    template_name = 'posts/follow.html'
    paginate_by = 10
    extra_context = {'follow': True}

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)


class ProfileFollowView(  # noqa: WPS215
    LoginRequiredMixin,
    PytestGetMixin,
    SameUserFollowMixin,
    View,
):
    """Подписка на автора."""

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=kwargs['username'])
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:follow_index')


class ProfileUnfollowView(  # noqa: WPS215
    LoginRequiredMixin,
    PytestGetMixin,
    SameUserFollowMixin,
    View,
):
    """Отписка от автора."""

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=kwargs['username'])
        request.user.follower.filter(author=author).delete()
        return redirect('posts:follow_index')
