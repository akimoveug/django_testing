from pytils.translit import slugify

from .fixtures import Test
from notes.models import Note
from notes.forms import WARNING


class TestLogic(Test):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
        }

    def create_note(self, user):
        """Функция создания заметки"""
        return user.post(self.NOTES_ADD, self.form_data)

    def test_authorized_user_can_create_note(self):
        """Тест возможности создавать заметку авторизованному пользователю"""
        notes_in_db = Note.objects.count()
        self.create_note(self.author_client)
        created_note = Note.objects.last()
        self.assertEqual(
            Note.objects.count(),
            notes_in_db + 1,
            msg='''Проверьте, что авторизованный пользователь может '''
                '''создавать заметки'''
        )
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)

    def test_anonimous_user_cant_create_note(self):
        """Тест, что неавторизованный пользователь не создаст заметку"""
        notes_in_db = Note.objects.count()
        self.create_note(self.client)
        self.assertEqual(
            Note.objects.count(),
            notes_in_db,
            msg='''Проверьте, что анонимный пользователь не может '''
                '''создавать заметки'''
        )

    def test_same_slug_in_notes(self):
        """Тест невозможности создать заметки с одинаковыми slug"""
        notes_in_db = Note.objects.count()
        for i in range(2):
            response = self.create_note(self.author_client)
        self.assertEqual(
            Note.objects.count(),
            notes_in_db + 1,
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            Note.objects.last().slug + WARNING
        )

    def test_slug_field_autocreate(self):
        """Тест того, что поле slug автоматически создаётся"""
        self.create_note(self.author_client)
        note = Note.objects.last()
        self.assertEqual(
            note.slug,
            slugify(self.form_data['title']),
            msg='''Проверьте что поле slug создаётся автоматически с '''
                '''помощью функции slugify()'''
        )

    def test_user_can_edit_own_note_and_cant_another_user(self):
        """Пользователи могут редактировать свои заметки, но не могут чужие"""
        for user in (self.author_client, self.auth_user_client):
            note = self.author.note_set.last()
            with self.subTest(user):
                user.post(self.NOTES_EDIT)
                updated_note = self.author.note_set.last()
                self.assertEqual(note.title, updated_note.title)
                self.assertEqual(note.text, updated_note.text)

    def test_user_can_delete_own_note_and_cant_another_user(self):
        """Пользователи могут удалять свои заметки, но не могут чужие"""
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
