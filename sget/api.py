import click


from sget import storage
from sget.snippet import Snippet
from sget.prompt import prompt


def get_all(group=None):
    collection = storage.get_all_snippets()
    if group is not None:
        return collection.get_group(group)
    else:
        return collection


def add(content, description, name, groups):
    storage.add_snippet(content, description, name, groups)


def fadd(snippet_file, description, name, groups):
    storage.add_snippet(''.join(snippet_file.readlines()),
                        description,
                        name,
                        groups)


def install(snippets_file):
    errors = storage.install_from_file(snippets_file)
    return errors


def get(name=None):
    snippet = _get_snippet(name)
    vars = snippet.get_vars()
    if len(vars) > 0:
        snippet = prompt.substitute_vars(snippet, vars)
    return snippet


def rm(name=None):
    snippet = _get_snippet(name)
    storage.rm_snippet(snippet)


def clear(name=None):
    storage.clear_snippets()


def _get_snippet(name=None):
    if not name:
        snippet = _query_snippet()
    else:
        snippet = storage.get_snippet(name)
    return snippet


def _query_snippet():
    snippets = storage.get_all_snippets()
    snippet = prompt.select_snippet(snippets)
    if not snippet:
        raise LookupError('No matching snippet found!')
    return snippet
