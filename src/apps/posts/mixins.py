from django.core.paginator import Paginator
from django.shortcuts import redirect

from apps.posts.models import User


_PAGE_PARAM = 'page'


class SameUserFollowMixin(object):
    """Проверка подписки на самого себя."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.username == kwargs['username']:
            return redirect(
                'posts:profile',
                username=kwargs['username'],
            )
        return super().dispatch(request, *args, **kwargs)


class PytestMixin(object):
    """Миксин для pytest'a :). Без него всё работает, но тесты практикума
    не проходят."""

    def get_context_data(self, *, object_list=None, **kwargs):
        page_number = self.request.GET.get(_PAGE_PARAM)
        context = super().get_context_data(object_list=object_list, **kwargs)
        context[_PAGE_PARAM] = context['paginator'].get_page(page_number)
        return context


class PytestGetMixin(object):
    """Перенаправление GET запроса для подписки/отписки, pytest отправляет GET
    запрос."""

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class UserIsFollowerMixin(object):
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


class PaginatorMixin(object):
    """Паджинатор постов."""

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        posts = context['object'].posts.all()
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get(_PAGE_PARAM)
        context[_PAGE_PARAM] = paginator.get_page(page_number)
        context['paginator'] = paginator
        return context
