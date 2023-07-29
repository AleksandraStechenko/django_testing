from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testauthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='testuser')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Test Note',
            'text': 'Test Note Text',
            'slug': 'test-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        """Тест: анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Тест: залогиненный пользователь может создать заметку."""
        self.user_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

    def test_duplicate_slug_not_allowed(self):
        """Тест: невозможно создать две заметки с одинаковым slug."""
        duplicate_form_data = self.form_data.copy()
        self.user_client.post(self.url, data=duplicate_form_data)
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertFormError(response,
                             form='form',
                             field='slug',
                             errors='test-slug' + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_auto_generate_slug(self):
        """Тест: slug формируется автоматически, если не был заполнен."""
        del self.form_data['slug']
        self.user_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):

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
                                       slug='test-slug',
                                       author=cls.author)
        cls.success_url = reverse('notes:success')
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.data = {'title': 'New Test Note',
                    'text': 'New Test Note Text',
                    'slug': 'new-test-slug'}

    def test_author_can_edit_note(self):
        """Тест: пользователь может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.text, self.data['text'])
        self.assertEqual(self.note.slug, self.data['slug'])

    def test_author_can_delete_note(self):
        """Тест: пользователь может удалить свою заметку."""
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_edit_note_of_another_user(self):
        """Тест: пользователь не может редактировать чужую заметку."""
        response = self.user_client.post(self.edit_url, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.data['title'])
        self.assertNotEqual(self.note.text, self.data['text'])
        self.assertNotEqual(self.note.slug, self.data['slug'])

    def test_user_cant_delete_note_of_another_user(self):
        """Тест: пользователь не может удалить чужую заметку."""
        response = self.user_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
