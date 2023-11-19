from django.views.generic import DetailView

from apps.posts.mixins import PaginatorMixin, UserIsFollowerMixin
from apps.posts.models import User


class ProfileView(PaginatorMixin, UserIsFollowerMixin, DetailView):
    """Профиль пользователя."""

    model = User
    template_name = 'posts/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
