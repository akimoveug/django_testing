from notes.forms import NoteForm
from .fixtures import Test


class TestContent(Test):
    def notes_list_context(self):
        return self.author_client.get(self.NOTES_LIST).context['object_list']

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
        reversed_urls = (self.NOTES_ADD, self.NOTES_EDIT)
        for reversed_url in reversed_urls:
            with self.subTest(reversed_url=reversed_url):
                self.assertIsInstance(
                    self.author_client.get(reversed_url).context['form'],
                    NoteForm,
                    msg=f'На страницу {reversed_url} не передаётся формa')
