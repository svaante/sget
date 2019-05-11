import click
import pyperclip


from snip import storage
from snip import share as _share
from snip.prompt import prompt


def list():
    for snippet in storage.get_all_snippets():
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
    try:
        storage.add_snippet(content, description, name, groups)
        return 'Successfully added snippet'
    except IOError as e:
        return str(e)


def fadd(snippet_file, description, name, groups):
    try:
        storage.add_snippet(''.join(snippet_file.readlines()),
                            description,
                            name,
                            groups)
        return 'Successfully added snippet'
    except IOError as e:
        return str(e)


def get(name=None):
    try:
        snippet = _get_snippet(name)
    except (FileNotFoundError, LookupError):
        raise LookupError('Snippet not found.')
    _snippet_to_clipboard(snippet)


def rm(name=None):
    try:
        snippet = _get_snippet(name)
    except (FileNotFoundError, LookupError):
        raise LookupError('Snippet not found')
    storage.rm_snippet(snippet)


def share(name=None):
    try:
        snippet = _get_snippet(name)
    except (FileNotFoundError, LookupError):
        raise LookupError('Snippet not found')
    return _share.share(snippet)


def clear(name=None):
    msg = 'You are about to clear all your saved snippets, are you sure?'
    if prompt.confirm(msg):
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
        raise LookupError('Could not find snippet')
    return snippet


def _snippet_to_clipboard(snippet):
    pyperclip.copy(snippet.content)
