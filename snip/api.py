import sys
import termios
import fcntl

import click
import pyperclip


from snip import storage
from snip.prompt import prompt


def list():
    for snippet in storage.get_all_snippets():
        msg = 'Description - {}'.format(snippet.description)
        click.echo(click.style(msg, fg='green'))
        msg = '    Snippet - {}'.format(snippet.content)
        click.echo(click.style(msg, fg='red'))
        click.echo('_' * 50)


def add(content, description, name):
    storage.add_snippet(content, description, name)


def cp(name=None):
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


def get(name=None):
    try:
        snippet = _get_snippet(name)
    except (FileNotFoundError, LookupError):
        raise LookupError('Snippet not found')
    _put_text_tty(snippet.content)


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
    snippet_contents = [s.content for s in snippets]
    snippet_content = prompt.select_snippet(snippet_contents)
    for snippet in snippets:
        if snippet.content == snippet_content:
            return snippet
    raise LookupError('Could not find snippet')


def _put_text_tty(text):
    tty = sys.stdin
    old_attr = termios.tcgetattr(tty)
    new_attr = termios.tcgetattr(tty)
    # No echo please
    new_attr[3] &= ~termios.ECHO
    termios.tcsetattr(tty, termios.TCSANOW, new_attr)

    for char in text:
        fcntl.ioctl(tty, termios.TIOCSTI, char)

    termios.tcsetattr(tty, termios.TCSANOW, old_attr)

def _snippet_to_clipboard(snippet):
    pyperclip.copy(snippet.content)
