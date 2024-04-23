from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.user = User.objects.create(username='Авторизованный пользователь')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'author': cls.author
        }
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user
        )

    def create_note(self, user):
        user.post(reverse('notes:add'), self.form_data)

    def test_authorized_user_can_create_note(self):
        self.create_note(self.auth_client)
        self.assertEqual(
            Note.objects.filter(author=self.user).count(),
            1,
            msg='''Проверьте, что авторизованный пользователь может '''
                '''создавать заметки'''
        )

    def test_anonimous_user_cant_create_note(self):
        total_notes = Note.objects.count(),
        self.create_note(self.client)
        self.assertEqual(
            Note.objects.count(),
            total_notes[0],
            msg='''Проверьте, что анонимный пользователь не может '''
                '''создавать заметки'''
        )

    def test_same_slug_in_notes(self):
        for i in range(2):
            self.create_note(self.auth_client)
        self.assertEqual(
            Note.objects.count(),
            1,
            msg='''Проверьте, что невозможно создать 2 заметки с '''
                '''одинаковыми slug'''
        )

    def test_slug_field_autocreate(self):
        self.create_note(self.auth_client)
        note = Note.objects.get()
        self.assertEqual(
            note.slug,
            slugify(self.form_data['title'])[:100],
            msg='''Проверьте что поле slug создаётся автоматически с '''
                '''помощью функции slugify()'''
        )

    def test_user_can_edit_delete_own_note_and_cant_another_user(self):
        Note.objects.create(title='Title3', text='Text', author=self.author)
        author_note = self.author.note_set.first()
        other_user_note = self.user.note_set.first()
        urls_statuses = (
            ('edit', author_note, HTTPStatus.OK),
            ('delete', author_note, HTTPStatus.FOUND),
            ('edit', other_user_note, HTTPStatus.NOT_FOUND),
            ('delete', other_user_note, HTTPStatus.NOT_FOUND),
        )

        for url, args, http_status in urls_statuses:
            with self.subTest(url=url):
                response = self.auth_client.post(
                    reverse('notes:' + url, args=[args.slug])
                )
                self.assertEqual(
                    response.status_code,
                    http_status,
                    msg='''Проверьте, что Авторизованный пользователь не '''
                    f'''может {url} запись пользователя {args.author}'''
                )
