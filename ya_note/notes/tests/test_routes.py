from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

        cls.NOTE_URLS = (
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )
        cls.NOTES_URLS = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )

        cls.USERS_URLS = (
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

    def page_available_for_user(self, users_statuses, urls):
        for user, status in users_statuses:
            if user:
                self.client.force_login(user)
            for url, args in urls:
                with self.subTest(url=url):
                    response = self.client.get(reverse(url, args=args))
                    self.assertEqual(
                        response.status_code,
                        status,
                        msg=f'Пользователю {user} недоступна страница {url}'
                    )

    def test_home_page(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            msg='Домашняя страница недоступна'
        )

    def test_availability_for_notes_list_add_success_for_auth_user(self):
        self.page_available_for_user(
            ((self.auth_user, HTTPStatus.OK),),
            self.NOTES_URLS
        )

    def test_availability_for_detail_edit_delete_pages(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.auth_user, HTTPStatus.NOT_FOUND),
        )
        self.page_available_for_user(users_statuses, self.NOTE_URLS)

    def test_redirect_for_anonymous_client(self):
        for url, args in self.NOTES_URLS + self.NOTE_URLS:
            with self.subTest(
                msg='''Проверьте, что анонимный пользователь переадресуется '''
                '''на страницу входа''',
                url=url
            ):
                page = reverse(url, args=args)
                self.assertRedirects(
                    self.client.get(page),
                    f'{reverse("users:login")}?next={page}'
                )

    def test_registration_login_logout_availability(self):
        users_statuses = (
            (self.auth_user, HTTPStatus.OK),
            (None, HTTPStatus.OK),
        )
        self.page_available_for_user(users_statuses, self.USERS_URLS)
