from django.views.generic import DetailView

from apps.posts.mixins import PaginatorMixin
from apps.posts.models import Group


class GroupView(PaginatorMixin, DetailView):
    """Страница группы."""

    model = Group
    template_name = 'posts/group.html'
