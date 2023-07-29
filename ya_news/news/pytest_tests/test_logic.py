import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, form_data, news_id_for_args
):
    """Тест: отправка комментария анонимным пользователем."""
    client.post(reverse('news:detail', args=(news_id_for_args)),
                data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        news_id_for_args, author_client, author, form_data
):
    """Тест: отправка комментария авторизованным пользователем."""
    author_client.post(reverse('news:detail',
                               args=(news_id_for_args)),
                       data=form_data)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(news_id_for_args, author_client, form_data):
    """Тест: запрещённые слова в комментарии."""
    form_data['text'] = f'Текст, {BAD_WORDS[0]}, текст.'
    response = author_client.post(
        reverse('news:detail', args=news_id_for_args), data=form_data
    )
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        comment_id_for_args, author_client, news_id_for_args
):
    """Тест: возможность автора удалять свои комментарии."""
    news_url = reverse('news:detail', args=news_id_for_args)
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        comment, author_client, comment_id_for_args,
        news_id_for_args, form_data
):
    """Тест: возможность автора редактировать свои комментарии."""
    news_url = reverse('news:detail', args=news_id_for_args) + '#comments'
    response = author_client.post(
        reverse('news:edit', args=(comment_id_for_args)), form_data
    )
    assertRedirects(response, news_url)
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == form_data['text']


def test_user_cant_delete_comment(comment_id_for_args, admin_client):
    """Тест: отсутствие возможности удалять чужие комментарии."""
    response = admin_client.delete(
        reverse('news:delete', args=(comment_id_for_args))
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_edit_comment(
        comment_id_for_args, admin_client,
        form_data, author, comment
):
    """Тест: отсутствие возможности редактировать чужие комментарии."""
    response = admin_client.post(
        reverse('news:edit', args=(comment_id_for_args)), form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
    assert comment.author == author
