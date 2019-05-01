import yaml
import os


class Snippet():
    def __init__(self, content, description, name):
        self._content = content
        self._description = description
        self._name = name

    @property
    def content(self):
        return self._content

    @property
    def description(self):
        return self._description

    @property
    def name(self):
        return self._name

    def to_yaml(self):
        return yaml.dump({'description': self._description,
                          'content': self._content})

    @staticmethod
    def from_file(f):
        f_name = os.path.basename(f)
        name = os.path.splitext(f_name)[0]
        with open(f, 'r') as snip_f:
            data = yaml.safe_load(snip_f.read())
        return Snippet(content=data['content'],
                       description=data['description'],
                       name=name)

    def __repr__(self):
        msg = 'Snippet:\ncontent - {}\ndescription - {}'
        return msg.format(self._content, self._description)
