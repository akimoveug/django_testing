import pytest

from http import HTTPStatus
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment


def detail_post(user, news, form_data):
    """Отправка комментария к отдельной новости."""
    return user.post(reverse('news:detail', args=[news.id]), form_data)


@pytest.mark.django_db
def test_anonimous_user_cant_send_comment(client, news, form_data):
    """Аноним не может отправить комментарий к новости."""
    detail_post(client, news, form_data)
    assert Comment.objects.count() == 0, (
        'Проверьте, что анонимный пользователь не может '
        'отправить комментарий'
    )


@pytest.mark.django_db
def test_auth_user_can_send_comment(author_client, news, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    detail_post(author_client, news, form_data)
    a=Comment.objects.count()
    assert Comment.objects.count() == 1, (
        'Проверьте, что авторизованный пользователь может '
        'отправить комментарий'
    )


def test_user_cant_use_bad_words(author_client, news, author):
    """Пользователь не может отправлять комментарий с плохими словами."""
    form_data = {
        'news': news,
        'text': f'Текст комментрария {BAD_WORDS[0]}',
    }
    response = detail_post(author_client, news, form_data)
    assert response.context['form'].is_valid() is False, (
        'Форма не валидна'
    )
    assert Comment.objects.count() == 0, (
        'Комментарии с плохими словами не должны создаваться'
    )


@pytest.mark.parametrize(
    'user, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('auth_user_client'), HTTPStatus.NOT_FOUND)
    ),
)
def test_users_can_edit_own_and_cant_another_user_comments(
    user, expected_status, comment, news
):
    """Проверка что пользователи могут редактировать свои/чужие комментарии."""
    response = user.post(reverse('news:edit', args=[news.id]))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'user, expected_status, total_comments_in_DB',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND, 0),
        (pytest.lazy_fixture('auth_user_client'), HTTPStatus.NOT_FOUND, 1)
    ),
)
def test_users_can_delete_own_and_cant_another_user_comments(
    user, expected_status, comment, news, total_comments_in_DB
):
    """Проверка что пользователи могут удалять свои/чужие комментарии."""
    response = user.delete(reverse('news:delete', args=[news.id]))
    assert response.status_code == expected_status
    assert Comment.objects.count() == total_comments_in_DB
