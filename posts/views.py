from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import (
    get_list_or_404,
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .mixins import (
    PostSuccessUrlMixin,
    PytestGetMixin,
    PytestMixin,
    SameUserFollowMixin,
    UserIsFollowerMixin,
)
from .models import Comment, Follow, Group, Post, User


@method_decorator(cache_page(20, key_prefix='index_page'), name='dispatch')
class IndexListView(PytestMixin, ListView):
    """Главная страница."""

    model = Post
    template_name = 'index.html'
    paginate_by = 10


class PostDetailView(UserIsFollowerMixin, DetailView):
    """Просмотр одного поста."""

    model = Post
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['form'] = CommentForm(self.request.POST or None)
        return data


class GroupListView(DetailView):
    """Страница группы."""

    model = Group
    template_name = 'group.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        posts = context['object'].posts.all()
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page'] = paginator.get_page(page_number)
        context['paginator'] = paginator

        return context


class NewPostCreateView(LoginRequiredMixin, CreateView):
    """Добавление нового поста."""

    model = Post
    template_name = 'new_post.html'
    form_class = PostForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class ProfileListView(UserIsFollowerMixin, ListView):
    """Профиль пользователя."""

    template_name = 'profile.html'
    paginate_by = 10

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        return author.posts.all()


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
                pk=self.kwargs['pk'],
            )
        return super().dispatch(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, PostSuccessUrlMixin, CreateView):
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

    template_name = 'follow.html'
    paginate_by = 10
    extra_context = {'follow': True}

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)


class ProfileFollowView(LoginRequiredMixin, PytestGetMixin, SameUserFollowMixin,
                        View):
    """Подписка на автора."""

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=kwargs['username'])
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('follow_index')


class ProfileUnfollowView(LoginRequiredMixin, PytestGetMixin,
                          SameUserFollowMixin, View):
    """Отписка от автора."""

    def post(self, request, *args, **kwargs):
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
