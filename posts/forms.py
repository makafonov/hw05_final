from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta(object):
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta(object):
        model = Comment
        fields = ('text', )
