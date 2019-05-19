import pytest
from prompt_toolkit.buffer import Document


from sget.prompt.search import SnippetSearcher
from sget.snippet import Snippet


SNIPPET_1 = Snippet(name='1foo_name',
                    content='1foo_content',
                    description='1foo_desc',
                    groups=['foo'])
SNIPPET_11 = Snippet(name='2foobar_name',
                    content='2foobar_content',
                    description='2foobar_desc',
                    groups=['foobar'])
SNIPPET_2 = Snippet(name='3foobaz_name',
                    content='3foobaz_content',
                    description='3foobaz_desc',
                    groups=['foobaz'])
SNIPPET_3 = Snippet(name='4foobarbaz_name',
                    content='4foobarbaz_content',
                    description='4foobarbaz_desc',
                    groups=['foobarbaz'])
SNIPPETS = [SNIPPET_1, SNIPPET_11, SNIPPET_2, SNIPPET_3]


def test_toggle_search_mode():
    searcher = SnippetSearcher([])
    assert searcher.search_mode == 'CONTENT'

    searcher.toggle_search_mode()
    assert searcher.search_mode == 'NAME'

    searcher.toggle_search_mode()
    assert searcher.search_mode == 'DESCRIPTION'

    searcher.toggle_search_mode()
    assert searcher.search_mode == 'CONTENT'


test_data = [('', 0, 4), ('foobar', 6, 2), ('foo', 3, 4),
             ('1fcont', 2, 1), ('2fcont', 2, 1), ('3fcont', 2, 1), ('4fcont', 2, 1),
             ('_cont', 5, 4), ('_name', 5, 0), ('_desc', 5, 0),
             ('bazcont', 3, 2), ('barcont', 3, 2)]
@pytest.mark.parametrize("text, cursor_pos, expected_len", test_data)
def test_get_completions_by_content(text, cursor_pos, expected_len):
    searcher = SnippetSearcher(SNIPPETS)

    doc = Document(text, cursor_position=cursor_pos)
    completions = list(searcher.get_completions(doc, None))
    assert len(list(completions)) == expected_len


test_data = [('', 0, 4), ('foobar', 6, 2), ('foo', 3, 4),
             ('1fname', 2, 1), ('2fname', 2, 1), ('3fname', 2, 1), ('4fname', 2, 1),
             ('_name', 5, 4), ('_cont', 5, 0), ('_desc', 5, 0),
             ('bazname', 3, 2), ('barname', 3, 2)]
@pytest.mark.parametrize("text, cursor_pos, expected_len", test_data)
def test_get_completions_by_name(text, cursor_pos, expected_len):
    searcher = SnippetSearcher(SNIPPETS)
    searcher.toggle_search_mode()

    doc = Document(text, cursor_position=cursor_pos)
    completions = list(searcher.get_completions(doc, None))
    assert len(list(completions)) == expected_len


test_data = [('', 0, 4), ('foobardesc', 6, 2), ('foodesc', 3, 4),
             ('1fdesc', 2, 1), ('2fdesc', 2, 1), ('3fdesc', 2, 1), ('4fdesc', 2, 1),
             ('_desc', 5, 4), ('_cont', 5, 0), ('_name', 5, 0),
             ('bazdesc', 3, 2), ('bardesc', 3, 2)]
@pytest.mark.parametrize("text, cursor_pos, expected_len", test_data)
def test_get_completions_by_description(text, cursor_pos, expected_len):
    searcher = SnippetSearcher(SNIPPETS)
    searcher.toggle_search_mode()
    searcher.toggle_search_mode()

    doc = Document(text, cursor_position=cursor_pos)
    completions = list(searcher.get_completions(doc, None))
    assert len(list(completions)) == expected_len


test_data = [('group=foo', 9, 1), ('group=foobar', 12, 1),
             ('group=foobaz', 12, 1), ('group=foobarbaz', 15, 1)]
@pytest.mark.parametrize("text, cursor_pos, expected_len", test_data)
def test_filter_group(text, cursor_pos, expected_len):
    searcher = SnippetSearcher(SNIPPETS)

    doc = Document(text, cursor_position=cursor_pos)
    completions = list(searcher.get_completions(doc, None))
    assert len(list(completions)) == expected_len
