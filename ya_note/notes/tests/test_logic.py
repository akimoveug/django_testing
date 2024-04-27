from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.fixtures import Test


class TestLogic(Test):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки'
        }

    def create_note(self, user):
        """Функция создания заметки."""
        return user.post(self.NOTES_ADD, self.form_data)

    def get_note(self):
        """Получаем объект заметки."""
        return Note.objects.get(id=self.author_note.id)

    def test_authorized_user_can_create_note(self):
        """Тест возможности создавать заметку авторизованному пользователю."""
        notes_in_db = Note.objects.count()
        self.create_note(self.author_client)
        created_note = Note.objects.last()
        self.assertEqual(
            Note.objects.count(),
            notes_in_db + 1,
            msg='''Проверьте, что авторизованный пользователь может'''
                ''' создавать заметки'''
        )
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)

    def test_anonimous_user_cant_create_note(self):
        """Тест, что неавторизованный пользователь не создаст заметку."""
        notes_in_db = Note.objects.count()
        self.create_note(self.client)
        self.assertEqual(
            Note.objects.count(),
            notes_in_db,
            msg='''Проверьте, что анонимный пользователь не может'''
                ''' создавать заметки'''
        )

    def test_same_slug_in_notes(self):
        """Тест невозможности создать заметки с одинаковыми slug."""
        notes_in_db = Note.objects.count()
        for _ in range(2):
            response = self.create_note(self.author_client)
        self.assertEqual(
            Note.objects.count(),
            notes_in_db + 1,
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            slugify(self.form_data['title']) + WARNING
        )

    def test_slug_field_autocreate(self):
        """Тест того, что поле slug автоматически создаётся."""
        self.create_note(self.author_client)
        note = Note.objects.last()
        self.assertEqual(
            note.slug,
            slugify(self.form_data['title']),
            msg='''Проверьте что поле slug создаётся автоматически с'''
                ''' помощью функции slugify()'''
        )

    def test_user_can_edit_own_note_and_cant_another_user(self):
        """Пользователи могут редактировать свои заметки, но не могут чужие.
        В тесте пытаемя изменить заметку автора из фикстур.
        """
        for user, expected_status, comment_must_change in (
            (self.author_client, HTTPStatus.FOUND, True),
            (self.auth_user_client, HTTPStatus.NOT_FOUND, False),
        ):
            with self.subTest(user):
                original_note = self.get_note()
                response = user.post(
                    self.NOTES_EDIT,
                    {'title': 'Новый заголовок', 'text': 'Новый текст'}
                )
                updated_note = self.get_note()
                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(
                    (original_note.title != updated_note.title),
                    comment_must_change
                )
                self.assertEqual(
                    (original_note.text != updated_note.text),
                    comment_must_change
                )

    def test_user_can_delete_own_note_and_cant_another_user(self):
        """Пользователи могут удалять свои заметки, но не могут чужие."""
        for user, expected_author_notes_change in (
            (self.author_client, 1),
            (self.auth_user_client, 0)
        ):
            with self.subTest(user):
                author_notes_count = self.author.note_set.count()
                user.delete(self.NOTES_DELETE)
                self.assertEqual(
                    self.author.note_set.count(),
                    author_notes_count - expected_author_notes_change
                )
