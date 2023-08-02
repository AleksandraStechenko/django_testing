import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment, News

HOME_URL = reverse('news:home')
User = get_user_model()


@pytest.mark.django_db
def test_news_count(client, create_news_data):
    """Тест: проверяет количество новостей на главной странице."""
    news_count = News.objects.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, create_news_data):
    """Тест: проверяет сортировку новостей. Свежие новости в начале списка."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, create_comment_data,
                        comment_detail_url):
    """Тест: проверяет сортировку комментариев в хронологическом порядке."""
    response = client.get(comment_detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    for i in range(1, Comment.objects.count()):
        assert all_comments[i - 1].created < all_comments[i].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_client_has_form(parametrized_client, form_on_page,
                         news_detail_url):
    """Тест: проверяет доступ к форме отправки комментария пользователю."""
    response = parametrized_client.get(news_detail_url)
    form_in_context = 'form' in response.context
    assert form_in_context is form_on_page
    if form_on_page:
        form = response.context['form']
        assert isinstance(form, CommentForm)
