import os


import toml


from snip.config import config as cfg
from snip.snippet import Snippet


def get_all_snippets():
    try:
        snippet_dicts = _get_snippet_dicts()
        snippets = [Snippet.from_dict(d, name)
                    for (name, d) in snippet_dicts.items()]
    except IOError:
        snippets = []
    return snippets


def add_snippet(content, description, name, groups):
    snippet = Snippet(content, description, name, groups)
    return _add_snippet(snippet)


def _add_snippet(snippet):
    snippet_dicts = _get_snippet_dicts()
    name = snippet.name
    if snippet_dicts.get(name) is not None:
        msg = 'Snippet with name {} already exists.'
        raise IOError(msg.format(name))

    with open(cfg.snippet_file, 'a') as f:
        f.write(toml.dumps(Snippet.to_dict(snippet)))



def get_snippet(name):
    snippets = _get_snippet_dicts()
    return Snippet.from_dict(snippets[name], name)


def rm_snippet(snippet):
    snippets = _get_snippet_dicts()
    del snippets[snippet.name]
    with open(cfg.snippet_file, 'w') as f:
        f.write(toml.dumps(snippets))


def clear_snippets():
    with open(cfg.snippet_file, 'w') as f:
        f.write('')


def install_from_file(input_file):
    snippet_dicts = toml.loads(input_file.read())
    snippets = [Snippet.from_dict(d, name)
                for (name, d) in snippet_dicts.items()]
    msgs = []
    for snippet in snippets:
        try:
            _add_snippet(snippet)
            msg = 'Successfully installed {}'
            msgs.append(msg.format(snippet.name))
        except IOError as e:
            msg = 'Error: could not add \'{}\', reason: {}'
            msgs.append(msg.format(snippet.name, str(e)))
    return msgs



def _get_snippet_dicts():
    with open(cfg.snippet_file, 'r') as f:
        data = toml.loads(f.read())
    return data
