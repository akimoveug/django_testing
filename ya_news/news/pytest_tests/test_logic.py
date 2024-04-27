from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError
from pytest_lazyfixture import lazy_fixture

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import (
    FORM_DATA, news_detail, UPDATED_FORM_DATA
)


def test_anonymous_user_cant_send_comment(client, news_detail_url):
    """Аноним не может отправить комментарий к новости."""
    comments_in_db = Comment.objects.count()
    news_detail(client.post, news_detail_url, FORM_DATA)

    assert Comment.objects.count() == comments_in_db, (
        'Проверьте, что анонимный пользователь не может '
        'отправить комментарий'
    )


def test_auth_user_can_send_comment(
        author_client, author, news, news_detail_url
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_in_db = Comment.objects.count()
    news_detail(author_client.post, news_detail_url, FORM_DATA)
    new_comment = Comment.objects.last()
    assert Comment.objects.count() == comments_in_db + 1, (
        'Проверьте, что авторизованный пользователь может '
        'отправить комментарий'
    )
    assert new_comment.text == FORM_DATA['text'], (
        'Текст созданного коментария не совпадает с отправленным'
    )
    assert new_comment.author == author, (
        f'У созданного коментария не тот автор - {new_comment.author}'
    )
    assert new_comment.news == news, (
        f'Комментарий добавлен не к той новости - {new_comment.news}'
    )


def test_user_cant_use_bad_words(author_client, news_detail_url):
    """Пользователь не может отправлять комментарий с плохими словами."""
    comments_in_db = Comment.objects.count()
    form_data = {
        'text': f'Текст комментария {choice(BAD_WORDS)}',
    }
    response = news_detail(author_client.post, news_detail_url, form_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == comments_in_db, (
        'Комментарии с плохими словами не должны создаваться'
    )


def test_users_can_edit_own_comment(
    author, author_client, comment, news_edit_url, news
):
    """Пользователь может изменить свой комментарий."""
    response = author_client.post(news_edit_url, UPDATED_FORM_DATA)
    updated_comment = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.FOUND
    assert updated_comment.news == news, 'Новость изменилась'
    assert updated_comment.author == author, 'Автор изменился'
    assert updated_comment.text == UPDATED_FORM_DATA['text'], (
        'Текст комментария не изменился'
    )


def test_user_cant_edit_another_user_comment(
    author, auth_user_client, comment, news_edit_url, news
):
    """Пользователь не может изменить чужой комментарий."""
    response = auth_user_client.post(news_edit_url, UPDATED_FORM_DATA)
    updated_comment = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert updated_comment.news == news, 'Новость изменилась'
    assert updated_comment.author == author, 'Автор изменился'
    assert updated_comment.text != UPDATED_FORM_DATA['text'], (
        'Текст комментария изменился'
    )


@pytest.mark.parametrize(
    'user, expected_status, total_comments_in_db',
    (
        (lazy_fixture('author_client'), HTTPStatus.FOUND, 0),
        (lazy_fixture('auth_user_client'), HTTPStatus.NOT_FOUND, 1)
    ),
)
def test_users_can_delete_own_and_cant_another_user_comments(
    user, expected_status, comment, total_comments_in_db, news_delete_url
):
    """Проверка что пользователи могут удалять свои/чужие комментарии."""
    response = user.delete(news_delete_url)
    assert response.status_code == expected_status
    assert Comment.objects.count() == total_comments_in_db
