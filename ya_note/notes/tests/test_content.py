from notes.forms import NoteForm
from notes.models import Note
from notes.tests.fixtures import Test


class TestContent(Test):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.auth_user_note = Note.objects.create(
            title='Заголовок заметки пользователя',
            text='Текст',
            author=cls.auth_user
        )

    def get_object_list(self):
        """Получаем список заметок из контекста."""
        return self.author_client.get(self.NOTES_LIST).context['object_list']

    def test_note_in_object_list(self):
        """Проверяем, что отдельная заметка передаётся на страницу со
        списком заметок в списке object_list словаря context.
        """
        self.assertIn(
            self.author_note,
            self.get_object_list(),
            msg='Заметка не передаётся в списке object_list'
        )

    def test_notes_list_only_by_its_author(self):
        """Проверяем, что в список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        self.assertQuerysetEqual(
            self.get_object_list(),
            self.author.note_set.all(),
            ordered=False,
            msg='В список заметок попадают заметки другого пользователя'
        )

    def test_create_update_contain_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        reversed_urls = (self.NOTES_ADD, self.NOTES_EDIT)
        for reversed_url in reversed_urls:
            with self.subTest(reversed_url=reversed_url):
                self.assertIsInstance(
                    self.author_client.get(reversed_url).context['form'],
                    NoteForm,
                    msg=f'На страницу {reversed_url} не передаётся формa')
