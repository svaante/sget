import os


import toml


from sget.config import config as cfg
from sget.snippet import Snippet


def get_all_snippets():
    snippet_dicts = _get_snippet_dicts()
    snippets = [Snippet.from_dict(d, name)
                for (name, d) in snippet_dicts.items()]
    return snippets


def add_snippet(content, description, name, groups):
    _make_root_dir()
    snippet = Snippet(content, description, name, groups)
    error = _add_snippets((snippet,))
    if error:
        raise IOError(error[0])


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
    errors = _add_snippets(snippets)
    return errors


def _add_snippets(snippets):
    snippets_dict = _get_snippet_dicts()
    errors = []
    for snippet in snippets:
        name = snippet.name
        if snippets_dict.get(name) is not None:
            msg = 'Could not add {}, name already exists.'
            errors.append(msg.format(name))
            continue
        snippets_dict[name] = Snippet.to_dict(snippet)

    with open(cfg.snippet_file, 'w') as f:
        f.write(toml.dumps(snippets_dict))
    return errors


def _get_snippet_dicts():
    try:
        with open(cfg.snippet_file, 'r') as f:
            data = toml.loads(f.read())
        return data
    except FileNotFoundError:
        return {}


def _make_root_dir():
    if not os.path.exists(cfg.root_dir):
        os.mkdir(cfg.root_dir)

