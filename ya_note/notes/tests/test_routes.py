from http import HTTPStatus

from notes.tests.fixtures import Test


class TestRoutes(Test):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.HOMEPAGE_USER_STATUS = (
            (cls.NOTES_HOME, (
                (cls.client, HTTPStatus.OK),
            )),
        )
        cls.PAGES_USERS_STATUSES = (
            (cls.NOTES_LIST, (
                (cls.author_client, HTTPStatus.OK),
            )),
            (cls.NOTES_SUCCESS, (
                (cls.author_client, HTTPStatus.OK),
            )),
            (cls.NOTES_ADD, (
                (cls.author_client, HTTPStatus.OK),
            )),
            (cls.NOTES_DETAIL, (
                (cls.author_client, HTTPStatus.OK),
                (cls.auth_user_client, HTTPStatus.NOT_FOUND),
            )),
            (cls.NOTES_EDIT, (
                (cls.author_client, HTTPStatus.OK),
                (cls.auth_user_client, HTTPStatus.NOT_FOUND),
            )),
            (cls.NOTES_DELETE, (
                (cls.author_client, HTTPStatus.OK),
                (cls.auth_user_client, HTTPStatus.NOT_FOUND),
            )),
        )
        cls.AUTH_PAGES_USERS_STATUSES = (
            (cls.USERS_LOGIN, ((cls.client, HTTPStatus.OK),)),
            (cls.USERS_LOGOUT, ((cls.client, HTTPStatus.OK),)),
            (cls.USERS_SIGNUP, ((cls.client, HTTPStatus.OK),)),
        )

    def test_pages_availability(self):
        """Тестирование доступности страниц для пользователей."""
        for reversed_url, users in (
            self.HOMEPAGE_USER_STATUS
            + self.PAGES_USERS_STATUSES
            + self.AUTH_PAGES_USERS_STATUSES
        ):
            for user, status in users:
                with self.subTest(reversed_url=reversed_url):
                    response = user.get(reversed_url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тестирование редиректа анонима."""
        for reversed_url, users in self.PAGES_USERS_STATUSES:
            with self.subTest(reversed_url=reversed_url):
                self.assertRedirects(
                    self.client.get(reversed_url),
                    f'{self.USERS_LOGIN}?next={reversed_url}'
                )
