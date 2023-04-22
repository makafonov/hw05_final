from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from posts.forms import CommentForm, PostForm
from posts.mixins import PytestMixin, UserIsFollowerMixin
from posts.models import Post


_CACHE_TIMEOUT = 20


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


class NewPostCreateView(LoginRequiredMixin, CreateView):
    """Добавление нового поста."""

    model = Post
    template_name = 'posts/new_post.html'
    form_class = PostForm
    success_url = reverse_lazy('posts:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    template_name = 'posts/new_post.html'
    form_class = PostForm
    extra_context = {'is_created': True}

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.username != self.kwargs['username']:
            return redirect(
                'posts:post',
                username=self.kwargs['username'],
                pk=self.kwargs['pk'],
            )
        return super().dispatch(request, *args, **kwargs)
