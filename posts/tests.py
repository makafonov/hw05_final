from urllib.parse import urljoin

from django.test import Client, TestCase
from django.urls import reverse

from .models import Post, User


class UserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sarah',
                                             email='connor.s@skynet.com',
                                             password='12345')
        self.post = Post.objects.create(text='Тестовый пост Сары!',
                                        author=self.user)
        self.client.force_login(self.user)
        self.anon_client = Client()

        self.urls_for_created_post = {
            'index':
                reverse('index'),
            'profile':
                reverse('profile', kwargs={'username': self.post.author}),
            'post':
                reverse('post',
                        kwargs={
                            'username': self.post.author,
                            'post_id': self.post.id
                        })
        }

    def test_user_profile(self):
        """
        После регистрации пользователя создается его персональная\
        страница (profile).
        """

        response = self.client.get(self.urls_for_created_post['profile'])
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username,
                         self.user.username)

    def test_authorized_user_create_new_post(self):
        """Авторизованный пользователь может опубликовать пост (new)."""

        response = self.client.post(
            reverse('new_post'),
            data={'text': 'Поехали!'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.urls_for_created_post['profile'])
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

        for url in self.urls_for_created_post.values():
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
                                    data={'text': modded_text},
                                    follow=True)
        for url in self.urls_for_created_post.values():
            response = self.client.get(url)
            self.assertContains(response, modded_text, status_code=200)

    def test_404_page(self):
        """
        Сервер возвращает код 404, если страница не найдена.
        """
        response = self.client.get('new_unknown_url/')
        self.assertEqual(response.status_code, 404)
