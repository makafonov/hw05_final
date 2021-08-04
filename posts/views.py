from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from posts.forms import CommentForm, PostForm
from posts.mixins import (
    PaginatorMixin,
    PytestGetMixin,
    PytestMixin,
    SameUserFollowMixin,
    UserIsFollowerMixin,
)
from posts.models import Comment, Follow, Group, Post, User


_CACHE_TIMEOUT = 20
_HTTP404 = 404
_HTTP500 = 500

@method_decorator(
    cache_page(_CACHE_TIMEOUT, key_prefix='index_page'),
    name='dispatch',
)
class IndexListView(PytestMixin, ListView):
    """Главная страница."""

    model = Post
    template_name = 'posts/index.html'
    paginate_by = 10


class PostDetailView(UserIsFollowerMixin, DetailView):
    """Просмотр одного поста."""

    model = Post
    template_name = 'posts/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(self.request.POST or None)
        return context


class GroupView(PaginatorMixin, DetailView):
    """Страница группы."""

    model = Group
    template_name = 'posts/group.html'


class NewPostCreateView(LoginRequiredMixin, CreateView):
    """Добавление нового поста."""

    model = Post
    template_name = 'posts/new_post.html'
    form_class = PostForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class ProfileView(PaginatorMixin, UserIsFollowerMixin, DetailView):
    """Профиль пользователя."""

    model = User
    template_name = 'posts/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'


class PostEditView(LoginRequiredMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    template_name = 'posts/new_post.html'
    form_class = PostForm
    extra_context = {'is_created': True}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.username != self.kwargs['username']:
            return redirect(
                'post',
                username=self.kwargs['username'],
                pk=self.kwargs['pk'],
            )
        return super().dispatch(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, CreateView):
    """Добавление комментария к посту."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        form.save()
        return super().form_valid(form)


class FollowIndexView(LoginRequiredMixin, PytestMixin, ListView):
    """Избранные авторы. Главная страница."""

    template_name = 'posts/follow.html'
    paginate_by = 10
    extra_context = {'follow': True}

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)


class ProfileFollowView(
    LoginRequiredMixin,
    PytestGetMixin,
    SameUserFollowMixin,
    View,
):
    """Подписка на автора."""

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=kwargs['username'])
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('follow_index')


class ProfileUnfollowView(
    LoginRequiredMixin,
    PytestGetMixin,
    SameUserFollowMixin,
    View,
):
    """Отписка от автора."""

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=kwargs['username'])
        request.user.follower.filter(author=author).delete()
        return redirect('follow_index')


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=_HTTP404,
    )


def server_error(request):
    return render(request, 'misc/500.html', status=_HTTP500)
