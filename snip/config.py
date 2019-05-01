import os


class Config():
    def __init__(self):
        self._snippet_dir_name = 'snippets'
        self._root_dir = os.path.expanduser('~/.snip')
        self._snippet_dir = os.path.join(self._root_dir,
                                         self._snippet_dir_name)

    @property
    def snippet_dir(self):
        return self._snippet_dir


config = Config()
