from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Edward')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тест',
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': [
                reverse('posts:'),
                reverse('posts:index')
            ],
            'posts/groups.html': reverse('posts:groups'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={
                    'username': self.post.author.username
                })
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={
                    'post_id': self.post.id
                })
            ),
            'posts/post_create.html': reverse('posts:post_create'),
            'posts/update_post.html': (
                reverse('posts:post_edit', kwargs={
                    'post_id': self.post.id
                })
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            if isinstance(reverse_name, list):
                for name in reverse_name:
                    with self.subTest(reverse_name=name):
                        response = self.authorized_client.get(name)
                        self.assertTemplateUsed(response, template)
            else:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        urls = ['', 'index']
        for url in urls:
            response = self.authorized_client.get(reverse(f'posts:{url}'))
            self.assertEqual(
                response.context['title'],
                'Последние обновления на сайте'
            )
            self.assertEqual(
                response.context['text'],
                'Добро пожаловать в Yatube! Говорим обо всем на свете'
            )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list',  kwargs={'slug': 'slug'})
        )
        self.assertEqual(response.context['group'], self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        )
        quantity = len(response.context['page_obj'])
        self.assertEqual(response.context['author'], self.post.author)
        self.assertEqual(response.context['quantity'], quantity)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        quantity = self.post.author.posts.count()
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['quantity'], quantity)

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_checking_render_on_page(self):
        """Проверка отображения поста на страницах."""
        url_names = [
            '/',
            '/index/',
            '/group/slug/',
            f'/profile/{self.post.author.username}/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.context['page_obj'][0], self.post)
                self.assertEqual(len(response.context['page_obj']), 1)
                if self.group != self.post.group:
                    self.assertNotEqual(response.context['page_obj'][0], self.post)


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Edward')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тест',
        )

    def test_index_page_contains_records(self):
        response = self.client.get(reverse('posts:'))
        self.assertEqual(len(response.context['page_obj']), 1)
        first_object = response.context['page_obj'][0]
        text = first_object.text
        group = first_object.group
        self.assertEqual(text, 'Тест')
        self.assertEqual(group, self.group)

    def test_group_list_page_contains_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        first_object = response.context['page_obj'][0]
        text = first_object.text
        group = first_object.group
        self.assertEqual(text, 'Тест')
        self.assertEqual(group, self.group)

    def test_profile_page_contains_records(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        first_object = response.context['page_obj'][0]
        text = first_object.text
        group = first_object.group
        self.assertEqual(text, 'Тест')
        self.assertEqual(group, self.group)
