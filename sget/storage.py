import os


import toml


from sget.config import config as cfg
from sget.snippet import Snippet, SnippetCollection


class Storage():
    def __init__(self, snippet_file):
        self._snippet_file = snippet_file

    def get_all_snippets(self):
        return SnippetCollection.from_dict(self._parse_snippet_file())

    def add_snippet(self, content, description, name, groups):
        snippet = Snippet(content, description, name, groups)
        error = self._add_snippets((snippet,))
        if error:
            raise IOError(error[0])

    def get_snippet(self, name, partial_match=True):
        collection = self.get_all_snippets()
        try:
            snippet = collection.get(name)
        except KeyError as e:
            if not partial_match:
                raise e
            snippet = self._find_by_partial_name(name, collection)
        return snippet

    def rm_snippet(self, name):
        collection = self.get_all_snippets()
        collection.rm(name)
        with open(self._snippet_file, 'w') as f:
            f.write(toml.dumps(collection.to_dict()))

    def clear_snippets(self):
        with open(self._snippet_file, 'w') as f:
            f.write('')

    def install_from_file(self, input_file):
        snippet_dicts = toml.loads(input_file.read())
        collection = SnippetCollection.from_dict(snippet_dicts)
        errors = self._add_snippets(collection)
        return errors

    def _find_by_partial_name(self, name, snippets):
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

    def _add_snippets(self, snippets):
        collection = self.get_all_snippets()
        errors = []
        for snippet in snippets:
            name = snippet.name
            if collection.exists(name):
                msg = 'Could not add {}, name already exists.'
                errors.append(msg.format(name))
                continue
            collection.add(snippet)

        with open(self._snippet_file, 'w') as f:
            f.write(toml.dumps(collection.to_dict()))
        return errors

    def _parse_snippet_file(self):
        try:
            with open(self._snippet_file, 'r') as f:
                data = toml.loads(f.read())
            return data
        except FileNotFoundError:
            return {}
