import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User


def year(request):
    """Добавляет переменную с текущим годом."""

    today = dt.datetime.today()
    year = today.year
    return {'year': year}


def index(request):
    post_list = Post.objects.select_related(
        'author').order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('author').filter(
        group=group).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html',
                  {'page': page, 'paginator': paginator, 'group': group})


@login_required
def new_post(request):
    """Добавление нового поста."""

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """Профиль пользователя."""

    author = get_object_or_404(User, username=username)
    post_list = author.posts.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'paginator': paginator
    })


def post_view(request, username, post_id):
    """Просмотр одного поста."""

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    return render(request, 'post.html', {
        'post': post,
        'author': post.author,
        'items': post.comments.all(),
        'form': form
    })


@login_required
def post_edit(request, username, post_id):
    """Редактирование поста."""

    if request.user.username != username:
        return redirect('index')
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new_post.html', {
        'form': form,
        'post': post,
        'is_created': True
    })


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post_id = post_id
        form.save()
    return redirect('post', username=username, post_id=post_id)
