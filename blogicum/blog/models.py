from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.urls import reverse


User = get_user_model()

TEXT_MAX = 30


class PostQuerySet(models.QuerySet):

    def filtered_posts(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )


class PublishedPostManager(models.Manager):

    def get_queryset(self):
        return (PostQuerySet(self.model).filtered_posts())


class PublishedModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published и дату публикации"""

    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
        ordering = ('created_at',)


class Category(PublishedModel):
    title = models.CharField(
        max_length=256, blank=False,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=False, verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True, blank=False,
        verbose_name='Идентификатор',
        help_text="Идентификатор страницы для URL; "
                  "разрешены символы латиницы, цифры, дефис и подчёркивание."
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=256, blank=False,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        default=timezone.now,
        blank=False,
        verbose_name='Дата и время публикации',
        help_text="Если установить дату и время в будущем — "
                  "можно делать отложенные публикации."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post',
        blank=False,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='post',
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        blank=False,
        verbose_name='Категория'
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    objects = PostQuerySet.as_manager()
    filtered_posts = PublishedPostManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # С помощью функции reverse() возвращаем URL объекта.
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class Comments(PublishedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments',
    )
    text = models.TextField('Текст комментария')

    class Meta:

        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:TEXT_MAX]


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)


#     def __str__(self):
#         return self.user.username
