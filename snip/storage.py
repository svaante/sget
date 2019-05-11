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


def _get_snippet_dicts():
    with open(cfg.snippet_file, 'r') as f:
        data = toml.loads(f.read())
    return data


def add_snippet(content, description, name, groups):
    snippet_dicts = _get_snippet_dicts()
    if snippet_dicts.get(name) is not None:
        msg = 'Snippet with name {} already exists.'
        raise IOError(msg.format(name))

    snippet = Snippet(content, description, name, groups)
    with open(cfg.snippet_file, 'a') as f:
        f.write(toml.dumps(Snippet.to_dict(snippet)))


def get_snippet(name):
    snippets = _get_snippet_dicts()
    return Snippet.from_dict(snippets[name], name)


def rm_snippet(snippet):
    snippet_path = os.path.join(cfg.snippet_dir, snippet.name) + '.snip'
    os.remove(snippet_path)


def clear_snippets():
    with open(cfg.snippet_file, 'w') as f:
        f.write('')
