from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit import print_formatted_text, HTML


def select_snippet(snippets):
    snippet_completer = FuzzyCompleter(SnippetCompleter(snippets))
    print('Type a description for your snippet, <Enter> to run it.')
    desc = prompt('> ', completer=snippet_completer)
    return desc


def confirm(msg):
    print_formatted_text(HTML('<red><b>{}</b></red>'.format(msg)))
    answer = prompt('[yes/no]: ')
    return answer.lower() == 'yes'


class SnippetCompleter(Completer):
    def __init__(self, descriptions):
        self._descriptions = descriptions

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for desc in self._descriptions:
            if desc.startswith(word):
                yield Completion(
                    desc,
                    start_position=-len(word),
                    style='fg:' + 'blue',
                    selected_style='fg:white bg:' + 'green')


def put_text(text):
    pass
