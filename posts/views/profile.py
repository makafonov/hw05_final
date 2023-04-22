from django.views.generic import DetailView

from posts.mixins import PaginatorMixin, UserIsFollowerMixin
from posts.models import User


class ProfileView(PaginatorMixin, UserIsFollowerMixin, DetailView):
    """Профиль пользователя."""

    model = User
    template_name = 'posts/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
