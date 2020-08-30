from django.core.paginator import Paginator
from django.shortcuts import redirect

from posts.models import User


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


class PytestGetMixin:
    """Перенаправление GET запроса для подписки/отписки, pytest отправляет GET
    запрос."""

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class UserIsFollowerMixin:
    """Добавление в контекст флага 'following' (является ли пользователь
    подписчиком)."""

    @property
    def extra_context(self):
        author = User.objects.get(username=self.kwargs['username'])

        following = False
        if self.request.user.is_authenticated:
            if self.request.user.follower.filter(author=author).exists():
                following = True
        return {
            'following': following,
            'author': author,
        }


class PaginatorMixin:
    """Паджинатор постов."""

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        posts = context['object'].posts.all()
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page'] = paginator.get_page(page_number)
        context['paginator'] = paginator
        return context
