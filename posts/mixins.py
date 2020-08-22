from django.shortcuts import redirect
from django.urls import reverse

from posts.models import User


class PostSuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            'post',
            kwargs={
                'username': self.kwargs['username'],
                'pk': self.kwargs['pk'],
            },
        )


class SameUserFollowMixin:
    """Проверка подписки на самого себя."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.username == kwargs['username']:
            return redirect(
                'profile',
                username=kwargs['username'],
            )
        return super().dispatch(request, *args, **kwargs)


class PytestMixin:
    """Миксин для pytest'a :). Без него всё работает, но тесты практикума
    не проходят."""

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
        author = User.objects.get(username=self.kwargs['username'])

        following = False
        if self.request.user.is_authenticated:
            if self.request.user.follower.filter(author=author).exists():
                following = True
        context['following'] = following
        context['author'] = author
        return context
