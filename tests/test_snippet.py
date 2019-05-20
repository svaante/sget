import pytest
import toml


from sget.snippet import Snippet, SnippetCollection


SNIPPETS = {'foo': {'content': 'foo',
                    'description': 'bar',
                    'groups': ['baz', 'bar']},
            'test': {'content': 'test',
                     'description': 'test',
                     'groups': ['baz']}}


def test_from_dict():
    name = 'foo'
    snippet = Snippet.from_dict(SNIPPETS[name], name=name)
    assert snippet.content == 'foo'
    assert snippet.description == 'bar'
    assert 'baz' in snippet.groups
    assert 'bar' in snippet.groups


def test_to_dict():
    name = 'foo'
    description = 'foobar'
    content = 'foobaz'
    groups = ['foo', 'baz']
    snippet = Snippet(name=name,
                      content=content,
                      description=description,
                      groups=groups)

    snippet_dict = snippet.to_dict()
    assert snippet_dict['content'] == content
    assert snippet_dict['description'] == description
    assert 'foo' in snippet_dict['groups']
    assert 'baz' in snippet_dict['groups']


def test_is_not_template():
    not_template = 'foo bar baz <b> <z>'
    assert not Snippet.is_template(not_template)


def test_is_template():
    template = 'foo bar baz <b> <z> <$>'
    assert Snippet.is_template(template)


def test_get_from_collection():
    collection = SnippetCollection()
    foo_snippet = Snippet.from_dict(SNIPPETS['foo'], 'foo')
    collection.add(foo_snippet)
    assert collection.get('foo') == foo_snippet


def test_collection_groups():
    collection = SnippetCollection.from_dict(SNIPPETS)
    assert 'baz' in collection.groups()
    assert 'bar' in collection.groups()


def test_collection_get_group():
    collection = SnippetCollection.from_dict(SNIPPETS)
    bar_snippets = collection.get_group('bar')
    assert bar_snippets.get('foo') != None
    with pytest.raises(KeyError):
        bar_snippets.get('test')

    baz_snippets = collection.get_group('baz')
    assert baz_snippets.get('foo') != None
    assert baz_snippets.get('test') != None


def test_collection_exists():
    collection = SnippetCollection.from_dict(SNIPPETS)
    assert collection.exists('foo')

def test_collection_not_exists():
    collection = SnippetCollection.from_dict(SNIPPETS)
    assert not collection.exists('not_exists')


def test_collection_add():
    collection = SnippetCollection.from_dict(SNIPPETS)
    snippet = Snippet.from_dict(SNIPPETS['foo'], 'foz')
    collection.add(snippet)

    assert collection.get('foz') == snippet


def test_collection_add_duplicate_name():
    collection = SnippetCollection.from_dict(SNIPPETS)
    snippet = Snippet.from_dict(SNIPPETS['foo'], 'foo')

    with pytest.raises(Exception):
        collection.add(snippet)


def test_collection_rm():
    collection = SnippetCollection.from_dict(SNIPPETS)
    collection.rm('foo')
    with pytest.raises(KeyError):
        collection.get('foo')
