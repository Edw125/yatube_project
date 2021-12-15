from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField('Группа', max_length=200)

    slug = models.SlugField('Идентификатор',
                            unique=True,
                            default='title',
                            max_length=200)
    description = models.TextField('Описание')

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='group_name',
        verbose_name='Группа',
        help_text='Выберите группу',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
