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

    def to_yaml(self):
        return yaml.dump({'description': self._description,
                          'content': self._content})

    @staticmethod
    def from_dict(data, name):
        content = data['content']
        description = data['description']
        groups = data.get('groups')
        return Snippet(content=content,
                       description=description,
                       name=name,
                       groups=groups)

    @staticmethod
    def to_dict(snippet):
        return {snippet.name: {'content': snippet.content,
                               'description': snippet.description,
                               'groups': snippet.groups}}

    def __repr__(self):
        msg = 'Snippet:\ncontent - {}\ndescription - {}'
        return msg.format(self._content, self._description)
