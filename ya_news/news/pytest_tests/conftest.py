from datetime import datetime, timedelta, timezone

import pytest
from django.conf import settings
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='Текст новости')
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def create_news_data():
    today = datetime.today()
    all_news = [
        News(
            title=f'Заголовок {index}',
            text='Текст новости.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comment_data(author, news):
    now = datetime.now(timezone.utc)
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def commment_form_data():
    return {
        'text': 'Текст комментария.'
    }


@pytest.fixture
def news_detail_url(news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def comment_detail_url(create_comment_data):
    return reverse('news:detail', args=(create_comment_data.id,))


@pytest.fixture
def comment_delete_url(comment_id_for_args):
    return reverse('news:delete', args=comment_id_for_args)


@pytest.fixture
def comment_edit_url(comment_id_for_args):
    return reverse('news:edit', args=(comment_id_for_args))
