from django.conf import settings

from news.forms import CommentForm
from .conftest import news_detail


def homepage_get_context(client, url):
    """Получение контекста с news:home."""
    return client.get(url).context['object_list']


def test_10_news_on_homepage(some_news, client, home_url):
    """Тестирование вывода новостей на главную страницу."""
    assert homepage_get_context(client, home_url).count(
    ) == settings.NEWS_COUNT_ON_HOME_PAGE, (
        'На главную страницу выводится неверное количество новостей'
    )


def test_news_sorting_on_homepage(some_news, client, home_url):
    """Тестирование сортировки новостей на главной странице по убыванию."""
    all_dates = [news.date for news in homepage_get_context(client, home_url)]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates, (
        'Новости на главной странице не сортируются по убыванию'
    )


def test_comments_sorting(client, news_detail_url):
    """Тестирование сортировки комментариев по возрастанию."""
    news = news_detail(client.get, news_detail_url).context['news']
    all_timestamps = [comment.created for comment in news.comment_set.all()]
    assert all_timestamps == sorted(all_timestamps), (
        'Комментарии к новости не отсортированы по возрастанию'
    )


def test_anonymous_client_has_no_form(client, news_detail_url):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    assert 'form' not in news_detail(client.get, news_detail_url).context, (
        'Анонимному пользователю не должна быть оступна форма '
        'для отправки комментария'
    )


def test_authorized_client_has_form(author_client, news_detail_url):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    response = news_detail(author_client.get, news_detail_url)
    assert 'form' in response.context, (
        'В контексте не передаётся форма'
    )
    assert isinstance(response.context['form'], CommentForm), (
        'form в контексте не является объектом класса ModelForm'
    )
