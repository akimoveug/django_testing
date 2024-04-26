from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture as lf
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status', (
        (lf('login_url'), lf('client'), HTTPStatus.OK),
        (lf('logout_url'), lf('client'), HTTPStatus.OK),
        (lf('signup_url'), lf('client'), HTTPStatus.OK),
        (lf('home_url'), lf('client'), HTTPStatus.OK),
        (lf('news_detail_url'), lf('client'), HTTPStatus.OK),
        (lf('news_edit_url'), lf('author_client'), HTTPStatus.OK),
        (lf('news_delete_url'), lf('author_client'), HTTPStatus.OK),
        (lf('news_edit_url'), lf('auth_user_client'), HTTPStatus.NOT_FOUND),
        (lf('news_delete_url'), lf('auth_user_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability(
    reverse_url, parametrized_client, expected_status, comment
):
    """Тестирование возможности попасть на страницы пользователями."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'reverse_url', lf(('news_edit_url', 'news_delete_url'))
)
def test_edit_delete_redirects_for_anonimous_user(
    client, reverse_url, login_url
):
    """Тестирование возможности анониму изменить или удалить комментарий."""
    response = client.get(reverse_url)
    assert response.status_code == HTTPStatus.FOUND, (
        'Неверный код ответа'
    )
    assertRedirects(
        response, expected_url=f'{login_url}?next={reverse_url}',
    )
