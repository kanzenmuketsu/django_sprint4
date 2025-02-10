from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()


class BasemodelClass(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Location(BasemodelClass, models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(BasemodelClass, models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(BasemodelClass, models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время '
                   'в будущем — можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        null=True,
        blank=False
    )
    image = models.ImageField(
        'Фото',
        blank=True,
        upload_to='post_images'
    )
    comment_count = models.IntegerField(
        verbose_name='Количество комментариев',
        null=False,
        blank=False,
        default=0
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        max_length=256
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text
