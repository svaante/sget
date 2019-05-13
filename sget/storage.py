import os


import toml


from sget.config import config as cfg
from sget.snippet import Snippet, SnippetCollection


def _make_root_dir():
    if not os.path.exists(cfg.root_dir):
        os.mkdir(cfg.root_dir)

_make_root_dir()


def get_all_snippets():
    collection = SnippetCollection.from_dict({'hehe': {'content': 'asd', 'description': 'hoho', 'groups': []}})
    return SnippetCollection.from_dict(_parse_snippet_file())


def add_snippet(content, description, name, groups):
    snippet = Snippet(content, description, name, groups)
    error = _add_snippets((snippet,))
    if error:
        raise IOError(error[0])


def get_snippet(name, partial_match=True):
    collection = get_all_snippets()
    try:
        snippet = collection.get(name)
    except KeyError as e:
        if not partial_match:
            raise e
        snippet = _find_by_partial_name(name, collection)
    return snippet


def rm_snippet(snippet):
    collection = get_all_snippets()
    collection.rm(snippet.name)
    with open(cfg.snippet_file, 'w') as f:
        f.write(toml.dumps(collection.to_dict()))


def clear_snippets():
    with open(cfg.snippet_file, 'w') as f:
        f.write('')


def install_from_file(input_file):
    snippet_dicts = toml.loads(input_file.read())
    collection = SnippetCollection.from_dict(snippet_dicts)
    errors = _add_snippets(collection)
    return errors


def _find_by_partial_name(name, snippets):
    candidates = []
    for snippet in snippets:
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
    collection = get_all_snippets()
    errors = []
    for snippet in snippets:
        name = snippet.name
        if collection.exists(name):
            msg = 'Could not add {}, name already exists.'
            errors.append(msg.format(name))
            continue
        collection.add(name, snippet)

    with open(cfg.snippet_file, 'w') as f:
        f.write(toml.dumps(collection.to_dict()))
    return errors


def _parse_snippet_file():
    try:
        with open(cfg.snippet_file, 'r') as f:
            data = toml.loads(f.read())
        return data
    except FileNotFoundError:
        return {}
