from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import News, Comment


FORM_DATA = {'text': 'Текст комментрария1'}


def news_detail(user_method, reversed_url, data=None):
    """Запрос к news:detail пользователем выбранным методом."""
    return user_method(reversed_url, data)


@pytest.fixture
def author(django_user_model):
    """Создание автора комментария."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def auth_user(django_user_model):
    """Создание пользователя."""
    return django_user_model.objects.create(
        username='Авторизованный пользователь'
    )


@pytest.fixture
def author_client(author):
    """Аутентификация автора комментария."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def auth_user_client(auth_user):
    """Аутентификация пользователя."""
    client = Client()
    client.force_login(auth_user)
    return client


@pytest.fixture
def news():
    """Создание новости."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, news):
    """Создание комментария к новости автором."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментрария',
    )


@pytest.fixture
def some_news():
    """Создание новостей для теста главной страницы."""
    today = datetime.today()

    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def news_edit_url(news):
    return reverse('news:edit', args=[news.id])


@pytest.fixture
def news_delete_url(news):
    return reverse('news:delete', args=[news.id])
