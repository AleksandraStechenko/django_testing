from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
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

    def test_user_notes_filter(self):
        """Тест списка заметок для пользователей."""
        clients = (
            (self.author_client, True),
            (self.user_client, False),
        )

        for client, should_contain_note in clients:
            with self.subTest(client=client):
                list_url = reverse('notes:list')
                response = client.get(list_url)
                note_list = response.context['object_list']
                self.assertIs(self.note in note_list, should_contain_note)

    def test_forms_on_pages(self):
        """Тест передачи формы на страницы создания и редактирования."""
        urls = (
            ('notes:add', None),
            ('notes:edit', self.slug,),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                form = response.context.get('form')
                self.assertIsNotNone(form)
                self.assertIsInstance(form, NoteForm)
