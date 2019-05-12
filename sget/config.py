import os


class Config():
    def __init__(self):
        self._snippet_file_name = 'snippets.toml'
        self._root_dir = os.path.expanduser('~/.snip')
        self._snippet_file = os.path.join(self._root_dir,
                                          self._snippet_file_name)

    @property
    def snippet_file(self):
        return self._snippet_file


config = Config()
