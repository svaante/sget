import os


import toml


from sget.config import config as cfg
from sget.snippet import Snippet


def _make_root_dir():
    if not os.path.exists(cfg.root_dir):
        os.mkdir(cfg.root_dir)

_make_root_dir()


def get_all_snippets():
    snippet_dicts = _get_snippet_dicts()
    snippets = [Snippet.from_dict(d, name)
                for (name, d) in snippet_dicts.items()]
    return snippets


def add_snippet(content, description, name, groups):
    snippet = Snippet(content, description, name, groups)
    error = _add_snippets((snippet,))
    if error:
        raise IOError(error[0])


def get_snippet(name):
    snippets = _get_snippet_dicts()
    try:
        snippet = Snippet.from_dict(snippets[name], name)
    except KeyError as e:
        snippet = _find_by_partial_name(name, snippets)
    return snippet


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


def _find_by_partial_name(name, snippets):
    candidates = []
    for snippet_name in snippets:
        snippet = Snippet.from_dict(snippets[snippet_name], snippet_name)
        if snippet.name.startswith(name):
            candidates.append(snippet)

    n_found = len(candidates)
    if n_found > 1:
        msg = 'Ambiguous name, found the following candidates:\n{}'
        candidates_str = '\n'.join((s.name for s in candidates))
        raise LookupError(msg.format(candidates_str))
    elif n_found == 0:
        msg = 'No snippet found with name {}!'
        raise LookupError(msg.format(name))

    return candidates[0]


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
