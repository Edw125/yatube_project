from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Edward')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст!',
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

    def test_models_verbose_name(self):
        """Проверяем, что у моделей корректно работает verbose_name."""
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

    def test_models_help_text(self):
        """Проверяем, что у моделей корректно работает help_text."""
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
