import tempfile
from io import BytesIO
from urllib.parse import urljoin

from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from PIL import Image
from sorl.thumbnail import get_thumbnail

from .models import Comment, Follow, Group, Post, User


class UserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.text = 'Тестовый пост Сары!'
        self.user = User.objects.create_user(username='sarah',
                                             email='connor.s@skynet.com',
                                             password='12345')
        self.group = Group.objects.create(slug='test', title='Test',
                                          description='test group')
        self.post = Post.objects.create(text=self.text,
                                        author=self.user,
                                        group=self.group)
        self.client.force_login(self.user)
        self.anon_client = Client()

        self.follower = User.objects.create_user(
            'username=terminator',
            email='terminator@skynet.com',
            password='best1',
        )
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

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
                            'post_id': post.id,
                        }),
            'group':
                reverse('group', kwargs={
                    'slug': self.group.slug,
                }),
        }
        if name:
            return urls[name]
        return urls

    @staticmethod
    def create_test_image_file():
        file = BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    @staticmethod
    def create_test_txt_file():
        file = BytesIO(b'Hello World')
        file.name = 'test.txt'
        file.seek(0)
        return file

    def test_user_profile(self):
        """
        После регистрации пользователя создается его персональная\
        страница (profile).
        """

        response = self.client.get(
            self.generate_urls_for_tests(name='profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username,
                         self.user.username)

    def test_authorized_user_create_new_post(self):
        """Авторизованный пользователь может опубликовать пост (new)."""

        response = self.client.post(
            reverse('new_post'),
            data={'text': 'Поехали!', 'group': self.group.id},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            self.generate_urls_for_tests(name='profile'))
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
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        url = urljoin(reverse('login'), '?next=' + reverse('new_post'))
        self.assertRedirects(response, url, status_code=302,
                             target_status_code=200, msg_prefix='',
                             fetch_redirect_response=True)

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
            kwargs={'username': self.post.author, 'post_id': self.post.id},
        )
        self.client.post(
            url,
            data={'text': modded_text, 'group': self.group.id},
            follow=True)

        for url in self.generate_urls_for_tests().values():
            if url == reverse('index'):
                cache.clear()
            response = self.client.get(url)
            self.assertContains(response, modded_text, status_code=200,
                                msg_prefix='Измененный текст не найден на '
                                           f'странице {url}. CACHE = '
                                           f'{settings.CACHES}')

    def test_404_page(self):
        """Сервер возвращает код 404, если страница не найдена."""

        response = self.client.get('unknown_url/')
        self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_page_with_image(self):
        """На страницах есть тэг img."""

        image = self.create_test_image_file()
        payload = {
            'group': self.group.id,
            'text': 'post with image',
            'image': image,
        }
        response = self.client.post(
            reverse('new_post'),
            data=payload,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name,
                         'index', msg='Пост не создался')
        self.assertEqual(Post.objects.all().count(), 2)

        latest_post = Post.objects.latest('pub_date')
        for url in self.generate_urls_for_tests(False, latest_post).values():
            if url == reverse('index'):
                cache.clear()
            response = self.client.get(url)
            img = get_thumbnail(
                latest_post.image, '783x339', crop='center', upscale=True)
            self.assertContains(response, img.url)

    def test_uploading_nonimage(self):
        """Защита от загрузки файлов не графических форматов."""

        file = self.create_test_txt_file()
        payload = {
            'group': self.group.id,
            'text': 'post with txt',
            'image': file,
        }
        response = self.client.post(
            reverse('new_post'),
            data=payload,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name,
                         'new_post', 'Пост создался')
        self.assertIsInstance(response.context['form'].errors, dict)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_cache_is_working(self):
        """Проверка работы кэша."""

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        text = 'Кэш есть'
        response = self.client.post(
            reverse('new_post'),
            data={'text': text},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, text, status_code=200)

    def test_authorized_user_create_comment(self):
        """Авторизированный пользователь может комментировать посты."""

        self.assertEqual(Comment.objects.all().count(), 0)
        comment = 'Комментарий'
        params = {'username': self.post.author, 'post_id': self.post.id}
        comment_url = reverse('add_comment', kwargs=params)
        response = self.client.post(
            comment_url,
            data={'text': comment},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.all().count(), 1)
        response = self.client.get(self.generate_urls_for_tests(name='post'))
        self.assertContains(response, comment, status_code=200)

    def test_unauthorized_user_create_comment(self):
        """Не авторизированный пользователь не может комментировать посты."""

        comment = 'Комментарий'
        params = {'username': self.post.author, 'post_id': self.post.id}
        comment_url = reverse('add_comment', kwargs=params)
        response = self.anon_client.post(
            comment_url,
            data={'text': comment},
            follow=True,
        )
        redirect_url = urljoin(reverse('login'), '?next=' + comment_url)
        self.assertRedirects(response, redirect_url, status_code=302,
                             target_status_code=200, msg_prefix='',
                             fetch_redirect_response=True)
        self.assertEqual(Comment.objects.all().count(), 0)
        response = self.client.get(self.generate_urls_for_tests(name='post'))
        self.assertNotContains(response, comment, status_code=200)

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может подписываться на других\
        пользователей."""

        self.assertEqual(self.follower.follower.all().count(), 0)
        follow_url = reverse('profile_follow', kwargs={'username': self.user})
        response = self.follower_client.get(follow_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.follower.follower.all().count(), 1)

    def test_authorized_user_can_unfollow(self):
        """Авторизованный пользователь может удлалять авторов из подписок."""

        Follow.objects.create(user=self.follower, author=self.user)
        self.assertEqual(self.follower.follower.all().count(), 1)
        unfollow_url = reverse('profile_unfollow',
                               kwargs={'username': self.user})
        response = self.follower_client.get(unfollow_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.follower.follower.all().count(), 0)

    def test_new_post_in_follow_index(self):
        """Новая запись пользователя появляется в ленте тех, кто на него\
        подписан."""

        Follow.objects.create(user=self.follower, author=self.user)
        self.assertEqual(self.follower.follower.all().count(), 1)
        response = self.follower_client.get(reverse('follow_index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('paginator', response.context)
        self.assertEqual(response.context['paginator'].count, 1)
        self.assertContains(response, self.text, status_code=200)

    def test_no_new_post_in_follow_index(self):
        """Новая запись пользователя не появляется в ленте тех, кто не\
        подписан на него."""

        response = self.follower_client.get(reverse('follow_index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('paginator', response.context)
        self.assertEqual(response.context['paginator'].count, 0)
        self.assertNotContains(response, self.text, status_code=200)
