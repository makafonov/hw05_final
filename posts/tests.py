import tempfile
from urllib.parse import urljoin

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from sorl.thumbnail import get_thumbnail

from .models import Post, User, Group
from django.db.models.fields.files import ImageFieldFile


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
})
class UserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sarah',
                                             email='connor.s@skynet.com',
                                             password='12345')
        self.group = Group.objects.create(slug='test', title='Test',
                                          description='test group')
        self.post = Post.objects.create(text='Тестовый пост Сары!',
                                        author=self.user,
                                        group=self.group)
        self.client.force_login(self.user)
        self.anon_client = Client()

    def generate_urls_for_tests(self, default=True, post=None, name=None):
        if default:
            post = self.post
        urls = {
            'index':
                reverse('index'),
            'profile':
                reverse('profile', kwargs={'username': post.author}),
            'post':
                reverse('post',
                        kwargs={
                            'username': post.author,
                            'post_id': post.id
                        }),
            'group':
                reverse('group', kwargs={
                    'slug': self.group.slug
                })
        }
        if name:
            return urls[name]
        return urls

    def test_user_profile(self):
        """
        После регистрации пользователя создается его персональная\
        страница (profile).
        """

        response = self.client.get(self.generate_urls_for_tests(name='profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username,
                         self.user.username)

    def test_authorized_user_create_new_post(self):
        """Авторизованный пользователь может опубликовать пост (new)."""

        response = self.client.post(
            reverse('new_post'),
            data={'text': 'Поехали!', 'group': self.group.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.generate_urls_for_tests(name='profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['paginator'].count, 2)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username,
                         self.user.username)

    def test_unauthorized_user_create_new_post(self):
        """
        Неавторизованный посетитель не может опубликовать пост\
        (его редиректит на страницу входа).
        """

        response = self.anon_client.post(
            reverse('new_post'),
            data={'text': 'Поехали!'},
            follow=True
        )
        self.assertEqual(Post.objects.count(), 1)
        url = urljoin(reverse('login'), '?next=' + reverse('new_post'))
        self.assertRedirects(
            response,
            url,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True
        )

    def test_create_new_post(self):
        """
        После публикации поста новая запись появляется на главной странице\
        сайта (index), на персональной странице пользователя\
        (profile), и на отдельной странице поста (post)
        """

        for url in self.generate_urls_for_tests().values():
            response = self.client.get(url)
            self.assertContains(response, self.post.text, status_code=200)

    def test_edit_post(self):
        """
        Авторизованный пользователь может отредактировать свой пост и его\
        содержимое изменится на всех связанных страницах
        """

        modded_text = 'Измененный пост'
        url = reverse(
            'post_edit',
            kwargs={'username': self.post.author, 'post_id': self.post.id}
        )
        response = self.client.post(url,
                                    data={'text': modded_text, 'group': self.group.id},
                                    follow=True)
        for url in self.generate_urls_for_tests().values():
            response = self.client.get(url)
            self.assertContains(response, modded_text, status_code=200)

    def test_404_page(self):
        """Сервер возвращает код 404, если страница не найдена."""

        response = self.client.get('new_unknown_url/')
        self.assertEqual(response.status_code, 404)

    def test_page_with_image(self):
        """На страницах есть тэг img."""

        with tempfile.TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                with open('posts/tests/test.jpg', 'rb') as img:
                    payload = {'group': self.group.id, 'text': 'post with image', 'image': img}
                    response = self.client.post(reverse('new_post'), data=payload, follow=True)
                    self.assertEqual(response.status_code, 200)
        latest_post = Post.objects.latest('pub_date')

        for url in self.generate_urls_for_tests(False, latest_post).values():
            response = self.client.get(url)
            self.assertContains(response, '<img', status_code=200)
            self.assertIsInstance(response.context['post'].image, ImageFieldFile)

            img = get_thumbnail(latest_post.image, "783x339", crop="center", upscale=True)
            self.assertContains(response, img.url)
