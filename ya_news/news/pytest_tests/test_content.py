import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def detail_get(user, news):
    """Запрос к news:detail."""
    return user.get(reverse('news:detail', args=[news.id]))


def homepage_get_context(client):
    """Получение контекста с news:home."""
    return client.get(reverse('news:home')).context['object_list']


@pytest.mark.django_db
def test_10_news_on_homepage(news10, client):
    """Тестирование вывода 10 новостей на главную страницу."""
    assert homepage_get_context(client).count(
    ) == settings.NEWS_COUNT_ON_HOME_PAGE, (
        'На главную страницу выводится не 10 новостей'
    )


@pytest.mark.django_db
def test_news_sorting_on_homepage(client):
    """Тестирование сортировки новостей на главной странице по убыванию."""
    all_dates = [news.date for news in homepage_get_context(client)]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates, (
        'Новости на главной странице не сортируются по убыванию'
    )


@pytest.mark.django_db
def test_comments_sorting(news, client):
    """Тестирование сортировки комментариев по возрастанию."""
    news = detail_get(client, news).context['news']
    all_timestamps = [comment.created for comment in news.comment_set.all()]
    assert all_timestamps == sorted(all_timestamps), (
        'Комментарии к новости не отсортированы по возрастанию'
    )


@pytest.mark.django_db
def test_anonymous_client_has_no_form(news, client):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    assert 'form' not in detail_get(client, news).context, (
        'Анонимному пользователю не должна быть оступна форма '
        'для отправки комментария'
    )


def test_authorized_client_has_form(author_client, news):
    """авторизованному пользователю доступна форма для отправки комментария."""
    response = detail_get(author_client, news)
    assert 'form' in response.context, (
        'В контексте не передаётся форма'
    )
    assert isinstance(response.context['form'], CommentForm), (
        'form в контексте не является объектом класса ModelForm'
    )
