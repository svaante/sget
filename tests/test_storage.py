import tempfile


import pytest
import toml


from sget.storage import Storage, AmbiguousNameError, NameNotFoundError


SNIPPETS = {'foo': {'content': 'foo',
                    'description': 'bar',
                    'groups': ['baz', 'bar']},
            'tmp': {'content': 'tmp',
                    'description': 'tmp',
                    'groups': ['tmp']}}

@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(mode='w+') as temp:
        temp.write(toml.dumps(SNIPPETS))
        temp.flush()
        yield temp.name


def _exists_in_file(snippet_file, name):
    with open(snippet_file, 'r') as f:
        snippets = toml.loads(f.read())
        return name in snippets.keys()


def test_get_all(temp_file):
    storage = Storage(temp_file)
    collection = storage.get_all_snippets()
    assert collection.get('foo') != None
    assert collection.get('foo').content == 'foo'

    snippet = collection.get('foo')
    assert snippet.content == 'foo'
    assert snippet.description == 'bar'
    assert 'baz' in snippet.groups
    assert 'bar' in snippet.groups


def test_add(temp_file):
    name = 'test_add'
    storage = Storage(temp_file)
    storage.add_snippet(content='fooz',
                        description='fooz',
                        name=name,
                        groups=['fooz'])
    assert _exists_in_file(temp_file, name)


def test_rm(temp_file):
    name = 'test_rm'
    storage = Storage(temp_file)
    storage.add_snippet(content='test_add',
                        description='test_add',
                        name=name,
                        groups=['test_add'])
    assert _exists_in_file(temp_file, name)
    storage.rm_snippet(name)
    assert not _exists_in_file(temp_file, name)


def test_clear(temp_file):
    name = 'test_rm'
    storage = Storage(temp_file)

    storage.clear_snippets()
    with open(temp_file, 'r') as f:
        data = f.read()
    assert data == ''


def test_get_snippet(temp_file):
    storage = Storage(temp_file)
    snippet = storage.get_snippet('tmp', partial_match=False)
    assert snippet.name == 'tmp'


def test_get_snippet_partial_name(temp_file):
    storage = Storage(temp_file)
    snippet = storage.get_snippet('fo', partial_match=True)
    assert snippet.name == 'foo'


def test_get_non_existent_name(temp_file):
    storage = Storage(temp_file)
    with pytest.raises(NameNotFoundError):
        storage.get_snippet('foobaz')


def test_get_ambiguous_name(temp_file):
    storage = Storage(temp_file)
    storage.add_snippet(content='fooz',
                        description='foz',
                        name='fooz',
                        groups=['foz'])
    with pytest.raises(AmbiguousNameError):
        storage.get_snippet('fo', partial_match=True)
