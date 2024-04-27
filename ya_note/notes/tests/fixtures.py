from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class Test(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_user = User.objects.create(username='Пользователь')
        cls.client = Client()
        cls.author_client = Client()
        cls.auth_user_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user_client.force_login(cls.auth_user)
        cls.author_note = Note.objects.create(
            title='Заметка автора',
            text='Текст',
            author=cls.author
        )

        cls.NOTES_HOME = reverse('notes:home')
        cls.NOTES_LIST = reverse('notes:list')
        cls.NOTES_SUCCESS = reverse('notes:success')
        cls.NOTES_ADD = reverse('notes:add')
        cls.NOTES_DETAIL = reverse('notes:detail', args=[cls.author_note.slug])
        cls.NOTES_EDIT = reverse('notes:edit', args=[cls.author_note.slug])
        cls.NOTES_DELETE = reverse('notes:delete', args=[cls.author_note.slug])
        cls.USERS_LOGIN = reverse('users:login')
        cls.USERS_LOGOUT = reverse('users:logout')
        cls.USERS_SIGNUP = reverse('users:signup')
