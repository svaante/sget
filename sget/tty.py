from sget.config import config


import termios
import subprocess
import os
import itertools
import sys
import shlex
import fcntl


def put_text(text, run=False):
    tty = sys.stdin
    old_attr = termios.tcgetattr(tty)
    new_attr = termios.tcgetattr(tty)
    new_attr[3] &= ~(termios.ECHO | termios.ICANON)
    termios.tcsetattr(tty, termios.TCSANOW, new_attr)
    for char in text:
        fcntl.ioctl(tty, termios.TIOCSTI, char)
    if run:
        fcntl.ioctl(tty, termios.TIOCSTI, '\n')

    termios.tcsetattr(tty, termios.TCSANOW, old_attr)


def edit(f_path):
    editor = _get_editor()
    cmd = '{} {}'.format(editor, f_path)
    subprocess.call(shlex.split(cmd))


def _get_editor():
    if config.editor != '':
        return config.editor
    elif os.environ.get('EDITOR'):
        return os.environ.get('EDITOR')
    elif os.environ.get('VISUAL'):
        return os.environ.get('VISUAL')

    known_editors = ('vim', 'vi', 'nano')
    locations = ('/usr/bin', '/usr/local/bin')
    for maybe_editor, location in itertools.product(known_editors, locations):
        editor_path = os.path.join(location, maybe_editor)
        if os.path.exists(editor_path):
            return editor_path
    else:
        msg = ("No available editor found, please specify an editor either in {} "
               "or as an environment variable EDITOR.").format(config.file)
        raise IOError(msg)
