import pytest

from http import HTTPStatus

from django.urls import reverse


@pytest.mark.parametrize(
    'page',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, page):
    """Тестирование возможности анониму попасть на главную страницу."""
    """и страницы входа, регистрации, выхода из аккуанта."""
    response = client.get(reverse(page))
    assert response.status_code == HTTPStatus.OK, (
         f'Анонимный пользователь должен попадать на страницу {page}'
    )


@pytest.mark.django_db
def test_news_detail_page_available_for_anonimous_user(client, news):
    """Тестирование возможности анониму попасть на страницу новости."""
    response = client.get(reverse('news:detail', args=[news.id]))
    assert response.status_code == HTTPStatus.OK, (
        'У анонимного пользователя должна быть возможность попасть '
        'на страницу отдельной новости'
    )


@pytest.mark.parametrize(
    'user, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('auth_user_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'url',
    ('news:edit', 'news:delete')
)
def test_availability_delete_update_comment_for_author_or_auth_user(
    user,  expected_status, url, news, comment
):
    """Тестируем возможность попасть на страницы редактирования."""
    """ и удаления коментариев (своих и чужих)."""
    response = user.get(reverse(url, args=[news.id]))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    ('news:edit', 'news:delete')
)
@pytest.mark.django_db
def test_edit_delete_redirects_for_anonimous_user(client, url, news):
    """Тестирование возможности анониму изменить или удалить комментарий."""
    page = reverse(url, args=[news.id])
    response = client.get(page)
    assert response.status_code == HTTPStatus.FOUND, (
        'Неверный код ответа'
    )
    assert response['Location'] == f'{reverse("users:login")}?next={page}', (
        'Неверная страница перенаправления'
    )
