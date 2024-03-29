import pytest
import tempfile


@pytest.fixture
def post(user):
    from apps.posts.models import Post
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Post.objects.create(text='Тестовый пост 1', author=user, image=image)


@pytest.fixture
def group():
    from apps.posts.models import Group
    return Group.objects.create(title='Тестовая группа 1', slug='test-link', description='Тестовое описание группы')


@pytest.fixture
def post_with_group(user, group):
    from apps.posts.models import Post
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Post.objects.create(text='Тестовый пост 2', author=user, group=group, image=image)
