import os

from snip.config import config as cfg
from snip.snippet import Snippet


def get_all_snippets():
    try:
        files = _get_all_snippets_from_dir(cfg.snippet_dir)
        snippets = [Snippet.from_file(f) for f in files]
    except IOError:
        snippets = []
    return snippets


def add_snippet(content, description, name=None):
    if not name:
        name = _get_next_snippet_name()
    snippet = Snippet(content.strip(), description.strip(), name.strip())
    snippet_path = os.path.join(cfg.snippet_dir, name + '.snip')
    with open(snippet_path, 'w+') as f:
        f.write(snippet.to_yaml())


def get_snippet(name):
    snippet_path = os.path.join(cfg.snippet_dir, name + '.snip')
    snippet = Snippet.from_file(snippet_path)
    return snippet


def rm_snippet(snippet):
    snippet_path = os.path.join(cfg.snippet_dir, snippet.name) + '.snip'
    os.remove(snippet_path)


def clear_snippets():
    for snippet in get_all_snippets():
        rm_snippet(snippet)


def _get_all_snippets_from_dir(dirr):
    if not os.path.isdir(dirr):
        raise IOError('No such directory {}'.format(dirr))
    snippet_paths = []
    for root, dirs, files in os.walk(dirr):
        snippet_paths = (os.path.join(root, f)
                         for f in files if f.endswith('.snip'))
    return snippet_paths


def _get_next_snippet_name():
    latest_id = -1
    snippet_files = _get_all_snippets_from_dir(cfg.snippet_dir)
    for snippet_path in snippet_files:
        try:
            snippet_name = os.path.basename(snippet_path)
            id = int(os.path.splitext(snippet_name)[0])
        except ValueError:
            continue
        if id > latest_id:
            latest_id = id
    return str(latest_id + 1)
