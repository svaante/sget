import sys
import termios
import fcntl

import click

from snip import storage
from snip import prompt


def list():
    for snippet in storage.get_all_snippets():
        msg = 'Description - {}'.format(snippet.description)
        click.echo(click.style(msg, fg='green'))
        msg = '    Snippet - {}'.format(snippet.content)
        click.echo(click.style(msg, fg='red'))
        click.echo('_' * 50)


def add(content, description):
    storage.add_snippet(content, description)


def rm():
    snippet = _query_snippet()
    if not snippet:
        return
    storage.rm_snippet(snippet)


def clear():
    msg = 'You are about to clear all your saved snippets, are you sure?'
    if prompt.confirm(msg):
        storage.clear_snippets()


def run():
    snippet = _query_snippet()
    if not snippet:
        return
    _put_text_tty(snippet.content)


def _query_snippet():
    snippets = storage.get_all_snippets()
    snippet_contents = [s.content for s in snippets]
    snippet_content = prompt.select_snippet(snippet_contents)
    for snippet in snippets:
        if snippet.content == snippet_content:
            return snippet


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
