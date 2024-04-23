import pytest

from django.test.client import Client

from news.models import News, Comment
from datetime import datetime, timedelta


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
def news10():
    """Создание 10 новостей для теста главной страницы."""
    today = datetime.today()

    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(11)
    )


@pytest.fixture
def form_data(news, author):
    """Заполненная форма."""
    return {
        'news': news,
        #'author': author,
        'text': 'Текст комментрария',
    }
