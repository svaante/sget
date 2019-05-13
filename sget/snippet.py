class Snippet():
    def __init__(self, content, description, name, groups=None):
        self._content = content
        self._description = description
        self._name = name
        if not groups:
            groups = []
        self._groups = groups

    @property
    def content(self):
        return self._content

    @property
    def description(self):
        return self._description

    @property
    def name(self):
        return self._name

    @property
    def groups(self):
        return self._groups

    def to_dict(self):
        return {'content': self.content,
                'description': self.description,
                'groups': self.groups}

    @staticmethod
    def from_dict(data, name):
        content = data['content']
        description = data['description']
        groups = data.get('groups')
        return Snippet(content=content,
                       description=description,
                       name=name,
                       groups=groups)

    def __repr__(self):
        msg = 'Snippet:\ncontent - {}\ndescription - {}'
        return msg.format(self._content, self._description)


class SnippetCollection():
    def __init__(self, snippets=None):
        self._lookup = {}
        for snippet in snippets or []:
            self._lookup[snippet.name] = snippet.to_dict()

    def __iter__(self):
        for name, snippet in self._lookup.items():
            yield Snippet.from_dict(snippet, name)

    def get(self, name):
        return Snippet.from_dict(self._lookup[name], name)

    def add(self, name, snippet, overwrite=False):
        if self._lookup.get(name) is not None and not overwrite:
            msg = 'Snippet with name {} already exists'
            raise ValueError(msg.format(name))
        self._lookup[name] = snippet.to_dict()

    def rm(self, name):
        del self._lookup[name]

    def exists(self, name):
        return self._lookup.get(name) is not None

    def to_dict(self):
        return self._lookup

    @staticmethod
    def from_dict(snippet_dict):
        collection = SnippetCollection()
        for name, snippet in snippet_dict.items():
            collection._lookup[name] = snippet
        return collection

