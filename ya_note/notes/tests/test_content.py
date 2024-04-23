from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

NOTES_LIST_URL = reverse('notes:list')

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_user = User.objects.create(username='Пользователь')
        for author in (cls.author, cls.auth_user):
            Note.objects.create(
                title=f'Заголовок {author}',
                text='Текст',
                author=author
            )
        cls.note = cls.author.note_set.all().first()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

    def notes_list_context(self):
        return self.auth_client.get(NOTES_LIST_URL).context['object_list']

    def test_note_in_object_list(self):
        self.assertIn(
            self.note,
            self.notes_list_context(),
            msg='Заметка не передаётся в списке object_list'
        )

    def test_notes_list_only_by_its_author(self):
        self.assertQuerysetEqual(
            self.notes_list_context(),
            self.author.note_set.all(),
            ordered=False,
            msg='В список заметок попадают заметки другого пользователя'
        )

    def test_create_update_contain_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for url, args in urls:
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.auth_client.get(
                        reverse(url, args=args)
                    ).context['form'],
                    NoteForm,
                    msg=f'На страницу {url} не передаётся формa')
