import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow


def year(request):
    """Добавляет переменную с текущим годом."""

    today = dt.datetime.today()
    current_year = today.year
    return {'year': current_year}


def index(request):
    """Главная страница."""

    post_list = Post.objects.select_related('author').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator, 'index': True})


def group_posts(request, slug):
    """Страница группы."""

    group = get_object_or_404(Group, slug=slug)
    posts = get_list_or_404(Post, group=group)
    paginator = Paginator(posts, 10)
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
    existing_follows = Follow.objects.filter(user=request.user)
    following = False
    for follow in existing_follows:
        if author.id == follow.author_id:
            following = True

    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'paginator': paginator,
        'following': following
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
    """Добавление комментария к посту."""

    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post_id = post_id
        form.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    """Избранные авторы. Главная страница"""

    # author_ids = Follow.objects.values_list('author_id').filter(
    #     user=request.user)
    # posts = Post.objects.filter(author_id__in=author_ids)
    posts = Post.objects.filter(author__in=request.user.follower.all().values_list('author'))
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator,
        'follow': True
    })


@login_required
def profile_follow(request, username):
    """Подписка на автора."""

    if request.user.username == username:
        return redirect('profile', username=username)
    new_author = get_object_or_404(User, username=username)
    follow = request.user.follower.all().filter(author=new_author)
    if not follow:
        Follow.objects.create(author_id=new_author.id, user_id=request.user.id)
        return redirect('follow_index')
    else:
        print('уже подписан')
        return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от графомана."""

    if request.user.username == username:
        return redirect('profile', username=username)
    existing_author = get_object_or_404(User, username=username)
    follow = request.user.follower.all().filter(author=existing_author)
    if follow:
        follow.delete()
        return redirect('follow_index')
    else:
        return redirect('profile', username=username)
