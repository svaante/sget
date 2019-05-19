import tempfile
import mock
from unittest.mock import MagicMock

import pytest
import toml
import pyperclip


from sget import api
from sget import prompt
from sget.snippet import Snippet
from sget.storage import Storage



SNIPPETS = {'1': {'content': '1',
                  'description': '1',
                  'groups': ['numbers']},
            '2': {'content': '2',
                  'description': '2',
                  'groups': ['numbers']},
            '35': {'content': '35',
                  'description': '35',
                  'groups': ['numbers']},
            '36': {'content': '36',
                  'description': '36',
                  'groups': ['numbers']},
            'a': {'content': 'a',
                   'description': 'a',
                   'groups': ['letters']}}

@pytest.fixture
def clean_storage():
    with tempfile.NamedTemporaryFile(mode='w+') as temp:
        temp.write(toml.dumps(SNIPPETS))
        temp.flush()
        storage = Storage(temp.name)
        api.STORAGE = storage
        yield


def test_get_all(clean_storage):
    collection = api.get_all()
    assert len(collection) == 5
    for name in SNIPPETS:
        assert collection.exists(name)


def test_get_all_groups(clean_storage):
    collection_numbers = api.get_all(group='numbers')
    assert len(collection_numbers) == 4
    assert not collection_numbers.exists('a')

    collection_letters = api.get_all(group='letters')
    assert len(collection_letters) == 1
    assert collection_letters.exists('a')


def test_cp(clean_storage):
    api.cp('1')
    assert pyperclip.paste() == '1'


def test_rm(clean_storage):
    api.rm('1')
    collection = api.get_all()
    assert not collection.exists('1')


mock_snippet = Snippet(name='3', description='bar', content='baz')
def mocked_prompt(*args):
    return mock_snippet


def test_run_prompts(clean_storage):
    @mock.patch('sget.tty.put_text', side_effect=None)
    @mock.patch('sget.prompt.prompt.select_snippet', side_effect=mocked_prompt)
    def test(select_snippet, put_text):
        api.run(mock_snippet.name)
        select_snippet.assert_called()
        put_text.assert_called_with(mock_snippet.content)

        select_snippet.reset()
        put_text.reset()

        api.run()
        select_snippet.assert_called()
        put_text.assert_called_with(mock_snippet.content)
    test()


def test_cp_prompts(clean_storage):
    @mock.patch('sget.prompt.prompt.select_snippet', side_effect=mocked_prompt)
    def test(select_snippet):
        api.cp(mock_snippet.name)
        select_snippet.assert_called()
        assert pyperclip.paste() == mock_snippet.content

        pyperclip.copy('')
        select_snippet.reset()

        api.cp()
        select_snippet.assert_called()
        assert pyperclip.paste() == mock_snippet.content
    test()


mock_rm_snippet = Snippet(name='35', description='bar', content='baz')
def mocked_rm_prompt(*args):
    return mock_rm_snippet

def test_rm_prompts(clean_storage):
    @mock.patch('sget.prompt.prompt.select_snippet', side_effect=mocked_rm_prompt)
    def test(select_snippet):
        api.rm(mock_rm_snippet.name[0:1])
        select_snippet.assert_called()

        select_snippet.reset()

        with pytest.raises(KeyError) as e:
            api.rm()
            assert str(e) == mock_rm_snippet.name
            select_snippet.assert_called()
    test()
