from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse_lazy

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
        for author in (cls.author, cls.auth_user):
            Note.objects.create(
                title=f'Заголовок {author}',
                text='Текст',
                author=author
            )
        cls.note = cls.author.note_set.last()

        cls.NOTES_HOME = reverse_lazy('notes:home')
        cls.NOTES_LIST = reverse_lazy('notes:list')
        cls.NOTES_SUCCESS = reverse_lazy('notes:success')
        cls.NOTES_ADD = reverse_lazy('notes:add')
        cls.NOTES_DETAIL = reverse_lazy('notes:detail', args=[cls.note.slug])
        cls.NOTES_EDIT = reverse_lazy('notes:edit', args=[cls.note.slug])
        cls.NOTES_DELETE = reverse_lazy('notes:delete', args=[cls.note.slug])
        cls.USERS_LOGIN = reverse_lazy('users:login')
        cls.USERS_LOGOUT = reverse_lazy('users:logout')
        cls.USERS_SIGNUP = reverse_lazy('users:signup')
