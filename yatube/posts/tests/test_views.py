import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Comment, Group, Post, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Edward')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
            self.assertEqual(
                response.context['page_obj'][0].image,
                self.post.image
            )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug'})
        )
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(response.context['author'], self.post.author)
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image
        )

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
        self.assertEqual(
            response.context['post'].image,
            self.post.image
        )

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
                    self.assertNotEqual(
                        response.context['page_obj'][0],
                        self.post
                    )


class PaginatorViewsTest(TestCase):
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
            text='Тест',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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


class PostCacheTests(TestCase):
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
            text='Тестовый текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_cache(self):
        """Проверка кеширования главной страницы."""
        urls = ['', 'index']
        for url in urls:
            response = self.authorized_client.get(
                reverse(f'posts:{url}')
            )
            Post.objects.filter(id=self.post.id).delete()
            response_cached = self.authorized_client.get(
                reverse(f'posts:{url}')
            )
            self.assertEqual(response.content, response_cached.content)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='Pushkin')
        cls.unfollower = User.objects.create_user(username='Edward')
        cls.author = User.objects.create_user(username='Leo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей."""
        count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists()
        )

    def test_authorized_user_can_unfollow(self):
        """Авторизованный пользователь может
         удалять пользователей из подписок."""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}))
        count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists()
        )

    def test_new_record_in_followers_feed(self):
        """Новая запись появляется в ленте подписчиков
        и не появляется в ленте тех, кто не подписан."""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}))

        self.authorized_client.logout()
        self.authorized_client.force_login(self.unfollower)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertFalse(response.context['page_obj'])

        self.authorized_client.logout()
        self.authorized_client.force_login(self.follower)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertTrue(response.context['page_obj'])

    def test_authorized_user_can_follow_once(self):
        """Подписаться на пользователя можно только один раз."""
        first_response = self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}))
        self.assertEqual(first_response.status_code, HTTPStatus.FOUND)
        second_response = self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}))
        self.assertEqual(second_response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), 1)


class CommentViewTest(TestCase):
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
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comments_checking_render_on_page(self):
        """Проверка отображения комментариев на странице post_detail."""
        response_authorized = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        response_guest = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response_authorized.context['comments'][0],
            self.comment
        )
        self.assertEqual(
            response_guest.context['comments'][0],
            self.comment
        )

    def test_comments_checking_add_by_authorized_user(self):
        """Проверка возможности комментировать посты
         авторизованным пользователем."""
        comment_count = Comment.objects.count()
        form_data = {
            'author': self.user,
            'post': self.post,
            'text': 'Тестовый комментарий',
        }
        response_authorized = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)

    def test_comments_checking_add_by_guest_user(self):
        """Проверка возможности комментировать посты
         анонимным пользователем."""
        comment_count = Comment.objects.count()
        form_data = {
            'author': self.user,
            'post': self.post,
            'text': 'Тестовый комментарий',
        }
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertEqual(response_guest.status_code, HTTPStatus.OK)
