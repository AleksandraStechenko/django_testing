from http import HTTPStatus
from random import choice

import pytest
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, commment_form_data,
        news_detail_url
):
    """Тест: отправка комментария анонимным пользователем."""
    expected_result = Comment.objects.count()
    client.post(news_detail_url,
                data=commment_form_data)
    assert Comment.objects.count() == expected_result


@pytest.mark.django_db
def test_user_can_create_comment(
        news_detail_url, author_client, author, commment_form_data
):
    """Тест: отправка комментария авторизованным пользователем."""
    expected_result = Comment.objects.count() + 1
    author_client.post(news_detail_url,
                       data=commment_form_data)
    assert Comment.objects.count() == expected_result


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    author_client,
    commment_form_data, news_detail_url
):
    """Тест: запрещённые слова в комментарии."""
    expected_result = Comment.objects.count()
    commment_form_data['text'] = f'Текст, {choice(BAD_WORDS)}, текст.'
    response = author_client.post(
        news_detail_url, data=commment_form_data
    )
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == expected_result


def test_author_can_delete_comment(
        comment_delete_url, author_client,
        news_detail_url
):
    """Тест: возможность автора удалять свои комментарии."""
    expected_result = Comment.objects.count() - 1
    url_to_comments = news_detail_url + '#comments'
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == expected_result


def test_author_can_edit_comment(
        comment, author_client, comment_edit_url,
        commment_form_data, news_detail_url
):
    """Тест: возможность автора редактировать свои комментарии."""
    news_url = news_detail_url + '#comments'
    original_news = comment.news
    original_author = comment.author
    commment_form_data['text'] = "Новый текст"
    response = author_client.post(
        comment_edit_url, commment_form_data
    )
    assertRedirects(response, news_url)
    comment.refresh_from_db()
    edited_news = comment.news
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == commment_form_data['text']
    assert original_author == comment.author
    assert original_news == edited_news


def test_user_cant_delete_comment(comment_delete_url, admin_client):
    """Тест: отсутствие возможности удалять чужие комментарии."""
    expected_result = Comment.objects.count()
    response = admin_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == expected_result


def test_user_cant_edit_comment(
        comment_edit_url, admin_client,
        commment_form_data, author, comment
):
    """Тест: отсутствие возможности редактировать чужие комментарии."""
    response = admin_client.post(
        comment_edit_url, commment_form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != commment_form_data['text']
    assert comment.author == author
