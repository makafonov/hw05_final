from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_list_or_404,
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


class PostSuccessUrlMixin:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_success_url(self):
        return reverse(
            'post',
            kwargs={
                'username': self.kwargs['username'],
                'post_id': self.kwargs['post_id'],
            },
        )


class SameUserFollowMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.username == kwargs['username']:
            return redirect(
                'profile',
                username=kwargs['username'],
            )
        return super().dispatch(request, *args, **kwargs)


class PytestMixin:
    """Миксин для pytest'a :). Без него всё работает,
    но тесты практикума не проходят."""
    def get_context_data(self, *, object_list=None, **kwargs):
        page_number = self.request.GET.get('page')
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['page'] = context['paginator'].get_page(page_number)
        return context


class UserIsFollowerMixin:
    """Добавление в контекст флага 'following' (является ли пользователь
    подписчиком)."""
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        following = False
        if self.request.user.is_authenticated:
            if self.request.user.follower.filter(author=self.author).exists():
                following = True
        context['following'] = following
        return context


@method_decorator(cache_page(20, key_prefix='index_page'), name='dispatch')
class IndexListView(PytestMixin, ListView):
    """Главная страница."""

    model = Post
    template_name = 'index.html'
    paginate_by = 10


class PostDetailView(UserIsFollowerMixin, DetailView):
    """Просмотр одного поста."""

    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form'] = CommentForm(self.request.POST or None)
        return data

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        self.author = post.author
        return post


class GroupListView(PytestMixin, ListView):
    """Страница группы."""

    template_name = 'group.html'
    paginate_by = 10

    def get_queryset(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])  # noqa
        return get_list_or_404(Post, group=self.group)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['group'] = self.group
        return context


class NewPostCreateView(LoginRequiredMixin, CreateView):
    """Добавление нового поста."""

    model = Post
    template_name = 'new_post.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('index')


class ProfileListView(UserIsFollowerMixin, ListView):
    """Профиль пользователя."""

    template_name = 'profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return self.author.posts.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['author'] = self.author
        return context


class PostEditView(LoginRequiredMixin, PostSuccessUrlMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    template_name = 'new_post.html'
    form_class = PostForm
    extra_context = {'is_created': True}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.username != self.kwargs['username']:
            return redirect(
                'post',
                username=self.kwargs['username'],
                post_id=self.kwargs['post_id'],
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Post, id=self.kwargs['post_id'])


class AddCommentView(LoginRequiredMixin, PostSuccessUrlMixin, CreateView):
    """Добавление комментария к посту."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        form.save()
        return super().form_valid(form)


class FollowIndexView(LoginRequiredMixin, PytestMixin, ListView):
    """Избранные авторы. Главная страница."""

    template_name = 'follow.html'
    paginate_by = 10
    extra_context = {'follow': True}

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)


class ProfileFollowView(LoginRequiredMixin, SameUserFollowMixin, View):
    """Подписка на автора."""
    def get(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=kwargs['username'])
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('follow_index')


class ProfileUnfollowView(LoginRequiredMixin, SameUserFollowMixin, View):
    """Отписка от автора."""
    def get(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=kwargs['username'])
        request.user.follower.filter(author=author).delete()
        return redirect('follow_index')


class PageNotFoundView(View):
    template_name = 'misc/404.html'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {'path': request.path},
            status=404,
        )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
