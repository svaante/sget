import click
import pyperclip


from sget import storage
from sget.prompt import prompt


def list(group=None):
    snippets = storage.get_all_snippets()
    if group:
        snippets = _filters_snippets_by_group(snippets, group)

    for snippet in snippets:
        name = 'Name - {}'.format(snippet.name)
        desc = 'Description - {}'.format(snippet.description)
        groups = 'Groups - {}'.format(snippet.groups)
        content = snippet.content
        click.echo(click.style(name, fg='green'))
        click.echo(click.style(desc, fg='green'))
        click.echo(click.style(groups, fg='green'))
        click.echo(click.style(content, fg='red'))
        click.echo('_' * 50)


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
    _snippet_to_clipboard(snippet)


def rm(name=None):
    snippet = _get_snippet(name)
    storage.rm_snippet(snippet)


def clear(name=None):
    msg = 'You are about to clear all your saved snippets, are you sure?'
    if prompt.confirm(msg):
        storage.clear_snippets()


def _filters_snippets_by_group(snippets, group):
    filtered = [s for s in snippets if group in s.groups]
    return filtered


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


def _snippet_to_clipboard(snippet):
    pyperclip.copy(snippet.content)
