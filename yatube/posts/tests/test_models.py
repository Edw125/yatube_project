from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Group, Post, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Edward')
        cls.author = User.objects.create_user(username='Leo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст!',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий',
        )
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        length_name = len(post.__str__())
        length = 15
        self.assertEqual(length_name, length)

        group = PostModelTest.group
        group_name = group.__str__()
        title = group.title
        self.assertEqual(group_name, title)

        comment = PostModelTest.comment
        length_name = len(comment.__str__())
        length = 15
        self.assertEqual(length_name, length)

        follow = PostModelTest.follow
        name = follow.__str__()
        self.assertEqual(name, f'Подписчик: {self.user}, автор:{self.author}')

    def test_model_post_verbose_name(self):
        """Проверяем, что у модели post корректно работает verbose_name."""
        post = PostModelTest.post
        field_verboses = {
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_model_comment_verbose_name(self):
        """Проверяем, что у модели comment корректно работает verbose_name."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name,
                    expected
                )

    def test_post_help_text(self):
        """Проверяем, что у модели post корректно работает help_text."""
        post = PostModelTest.post
        field_help_text = {
            'group': 'Выберите группу',
            'text': 'Введите текст поста',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text,
                    expected
                )

    def test_comment_help_text(self):
        """Проверяем, что у модели comment корректно работает help_text."""
        comment = PostModelTest.comment
        field_help_text = {
            'text': 'Введите текст комментария',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text,
                    expected
                )
