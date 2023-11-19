from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from apps.posts.forms import CommentForm
from apps.posts.models import Comment


class AddCommentView(LoginRequiredMixin, CreateView):
    """Добавление комментария к посту."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        form.save()
        return super().form_valid(form)
