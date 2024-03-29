from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


_TITLE_MAX_LENGTH = 200

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=_TITLE_MAX_LENGTH)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(verbose_name='Текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name='Дата публикации поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
    )
    image = models.ImageField(
        upload_to='posts/', blank=True, null=True, verbose_name='Изображение',
    )

    class Meta(object):
        ordering = ['-pub_date']

    def __str__(self):
        return self.text

    def get_header(self):
        return ' '.join(self.text.split()[:5])

    def get_absolute_url(self):
        return reverse('posts:post', kwargs={'pk': self.pk, 'username': self.author})


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
    )
    text = models.TextField()
    created = models.DateTimeField('comment created date', auto_now_add=True)

    def get_absolute_url(self):
        return reverse(
            'posts:post',
            kwargs={
                'pk': self.post.pk,
                'username': self.post.author,
            },
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
    )

    class Meta(object):
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_not_author',
            ),
        ]
