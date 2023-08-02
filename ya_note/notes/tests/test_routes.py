from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testauthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='testuser')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(title='Test Note',
                                       text='Test Note Text',
                                       author=cls.author)
        cls.slug = (cls.note.slug,)

    def test_pages_availability(self):
        """Тест доступа страниц пользователям."""
        urls = (
            ('notes:home', None, self.client, HTTPStatus.OK),
            ('users:login', None, self.client, HTTPStatus.OK),
            ('users:logout', None, self.client, HTTPStatus.OK),
            ('users:signup', None, self.client, HTTPStatus.OK),
            ('notes:detail', self.slug, self.author_client, HTTPStatus.OK),
            ('notes:edit', self.slug, self.author_client, HTTPStatus.OK),
            ('notes:delete', self.slug, self.author_client, HTTPStatus.OK),
            ('notes:list', None, self.user_client, HTTPStatus.OK),
            ('notes:add', None, self.user_client, HTTPStatus.OK),
            ('notes:success', None, self.user_client, HTTPStatus.OK),
            (
                'notes:detail', self.slug,
                self.user_client, HTTPStatus.NOT_FOUND
            ),
            (
                'notes:edit', self.slug,
                self.user_client, HTTPStatus.NOT_FOUND
            ),
            (
                'notes:delete', self.slug,
                self.user_client, HTTPStatus.NOT_FOUND
            ),
        )

        for name, args, client, http_status in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = client.get(url)
                self.assertEqual(response.status_code, http_status)

    def test_redirect_for_anonymous_client(self):
        """Тест перенаправления на страницу логина."""
        login_url = reverse('users:login')
        redirect_urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', self.slug),
            ('notes:edit', self.slug),
            ('notes:delete', self.slug),
        )

        for name, args in redirect_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
