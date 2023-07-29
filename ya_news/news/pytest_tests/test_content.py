import pytest
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_news_count(client, create_news_data):
    """Тест: проверяет количество новостей на главной странице."""
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, create_news_data):
    """Тест: проверяет сортировку новостей. Свежие новости в начале списка."""
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, create_comment_data):
    """Тест: проверяет сортировку комментариев в хронологическом порядке."""
    response = client.get(reverse('news:detail', args=(create_comment_data.id,)))
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_client_has_form(parametrized_client, form_on_page, news_id_for_args):
    """Тест: проверяет доступ к форме отправки комментария пользователю."""
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    form_in_context = 'form' in response.context
    assert form_in_context is form_on_page
