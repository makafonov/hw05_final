from django.views.generic import DetailView

from posts.mixins import PaginatorMixin
from posts.models import Group


class GroupView(PaginatorMixin, DetailView):
    """Страница группы."""

    model = Group
    template_name = 'posts/group.html'
