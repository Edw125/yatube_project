from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_url(self):
        """Страница доступна любому пользователю."""
        url_names = [
            '/',
            '/index/',
            '/group/slug/',
            f'/profile/{self.post.author.username}/',
            f'/posts/{self.post.id}/',
            # Pytest проходит локально, но yandex не пускает этот url
            # '/unexisting_page',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_authorized(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_for_author(self):
        """Страница доступна автору поста."""
        user = self.user.username
        author = self.post.author.username
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        if author == user:
            self.assertEqual(response.status_code, HTTPStatus.OK)
        else:
            self.assertEqual(user, author)

    def test_post_url_redirect_anonymous(self):
        """Страница перенаправляет анонимного пользователя на страницу."""
        url_names = [
            '/create/',
            f'/posts/{self.post.id}/edit/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={address}'
                )

    def test_post_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/index/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/update_post.html',
            '/create/': 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
