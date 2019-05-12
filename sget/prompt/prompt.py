from prompt_toolkit.completion import Completion, FuzzyCompleter
from prompt_toolkit.completion.fuzzy_completer import _FuzzyMatch
from prompt_toolkit.lexers import DynamicLexer
from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import prompt, PromptSession
from prompt_toolkit.shortcuts.prompt import _split_multiline_prompt
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.menus import _get_menu_item_fragments
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.controls import (
    BufferControl,
    FormattedTextControl,
    UIControl,
    UIContent
)
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings, KeyBindings
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.filters import has_focus, is_done, Condition, renderer_height_is_known
from prompt_toolkit.layout.processors import DynamicProcessor, merge_processors

from functools import partial
import re


def select_snippet(snippets):
    snippet_completer = SnippetCompleter(snippets)
    session = SplitPromptSession()
    snippet_meta = session.prompt(HTML('> '), completer=snippet_completer)
    snippet_meta, _ = _strip_prefix(snippet_meta)
    snippet_meta = snippet_meta.strip()
    for snippet in snippets:
        if _match(snippet, snippet_meta):
            return snippet


def _strip_prefix(word):
    prefix = word[0:2]
    if len(prefix) < 2 or prefix not in CATEGORY_MATCHERS.keys():
        return word, ''
    else:
        return word[2:], prefix


def _match(snippet, snippet_meta):
    return (snippet.content == snippet_meta
            or snippet.description == snippet_meta
            or snippet.name == snippet_meta)


def confirm(msg):
    print_formatted_text(HTML('<red><b>{}</b></red>'.format(msg)))
    answer = prompt('[yes/no]: ')
    return answer.lower() == 'yes'


class SplitPromptSession(PromptSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bottom_toolbar = self.update_toolbar_text

    def _create_layout(self):
        """
        Create `Layout` for this prompt.
        """
        dyncond = self._dyncond

        # Create functions that will dynamically split the prompt. (If we have
        # a multiline prompt.)
        has_before_fragments, get_prompt_text_1, get_prompt_text_2 = \
            _split_multiline_prompt(self._get_prompt)

        default_buffer = self.default_buffer
        search_buffer = self.search_buffer

        all_input_processors = [
            DynamicProcessor(lambda: merge_processors(self.input_processors or [])),
        ]

        default_buffer_control = BufferControl(
            buffer=default_buffer,
            search_buffer_control=None,
            input_processors=all_input_processors,
            include_default_input_processors=False,
            lexer=DynamicLexer(lambda: self.lexer),
            preview_search=True)

        prompt_window = Window(FormattedTextControl(get_prompt_text_1),
                               dont_extend_height=True)
        default_buffer_window = Window(
            default_buffer_control,
            dont_extend_height=True,
            get_line_prefix=partial(
                self._get_line_prefix, get_prompt_text_2=get_prompt_text_2),
            wrap_lines=dyncond('wrap_lines'))
        divider = Window(char='.', height=1, style='bg:black')
        completion_window = Window(content=CompletionsWidgetControl(),
                style='')
        bottom_toolbar = ConditionalContainer(
            Window(FormattedTextControl(
                        lambda: self.bottom_toolbar),
                        #style='class:bottom-toolbar.text'),
                   #style='class:bottom-toolbar',
                   dont_extend_height=True,
                   height=Dimension(min=1)),
            filter=~is_done & renderer_height_is_known &
                    Condition(lambda: self.bottom_toolbar is not None))


        # Build the layout.
        layout = HSplit([
            prompt_window,
            default_buffer_window,
            divider,
            completion_window,
            bottom_toolbar
        ])

        return Layout(layout, default_buffer_window)

    def _create_application(self, editing_mode, erase_when_done):
        """
        Create the `Application` object.
        """
        dyncond = self._dyncond

        # Default key bindings.
        prompt_bindings = self._create_prompt_bindings()
        search_mode_bindings = self._create_search_mode_bindings()

        # Create application
        application = Application(
            layout=self.layout,
            full_screen=True,
            key_bindings=merge_key_bindings([
                merge_key_bindings([
                    prompt_bindings,
                    search_mode_bindings
                ]),
            ]),
            color_depth=lambda: self.color_depth,
            input=self.input,
            output=self.output)

        return application


    def _create_search_mode_bindings(self):
        key_bindings = KeyBindings()
        handle = key_bindings.add
        default_focused = has_focus(DEFAULT_BUFFER)

        @handle('c-m', filter=default_focused)
        def _(event):
            buf = event.current_buffer
            self.completer.toggle_search_mode()
            buf.complete_state = None
            buf.start_completion()
            self.update_toolbar_text()
        return key_bindings

    def update_toolbar_text(self):
            toolbar_text = []
            for i, search_mode in enumerate(self.completer.SEARCH_MODE_NAMES):
                if i == self.completer._search_mode_idx:
                    style_class = 'fg:green'
                else:
                    style_class = 'fg:gray'
                toolbar_text.append((style_class, search_mode))
                toolbar_text.append(('fg:gray', '  |  '))
            return toolbar_text[0:-1]


class CompletionsWidgetControl(UIControl):
    def has_focus(self):
        return False

    def create_content(self, width, height):
        complete_state = get_app().current_buffer.complete_state
        if complete_state:
            completions = complete_state.completions
            completion_index = complete_state.complete_index
        else:
            completions = []
            completion_index = -1

        def get_line(idx):
            completion = completions[idx]
            is_curr_completion = (idx == completion_index)
            return _get_menu_item_fragments(completion,
                                            is_curr_completion,
                                            width)
        return UIContent(get_line, line_count=len(completions))


def _content_match(snippet, word):
    if snippet.content.startswith(word):
        return snippet.content
    return None


def _name_match(snippet, word):
    if snippet.name.startswith(word):
        return snippet.name
    return None


def _description_match(snippet, word):
    if snippet.description.startswith(word):
        return snippet.description
    return None


def _filter_by_group(snippets, filter_groups):
    for snippet in snippets:
        for group in snippet.groups:
            if group in filter_groups:
                yield snippet
                break


class SnippetCompleter(FuzzyCompleter):
    SEARCH_MODES = (_content_match, _name_match, _description_match)
    SEARCH_MODE_NAMES = ('CONTENT', 'NAME', 'DESCRIPTION')

    def __init__(self, snippets):
        super(SnippetCompleter).__init__()
        self._snippets = snippets
        self._search_mode_idx = -1
        self.toggle_search_mode()

    def toggle_search_mode(self):
        next_idx = (self._search_mode_idx + 1) % len(SnippetCompleter.SEARCH_MODES)
        self._search_mode_idx = next_idx
        self._match = SnippetCompleter.SEARCH_MODES[next_idx]

    def get_search_mode_name(self):
        return SEARCH_MODE_NAMES[self._search_mode_idx]

    def get_completions(self, doc, event):
        prompt_content = doc.text_before_cursor
        text, groups = self._parse_group_filters(prompt_content)
        offset = len(prompt_content) - len(text)
        doc_text = doc.text[offset:doc.cursor_position - len(text)]
        cursor_pos = doc.cursor_position - len(text) - offset
        doc2 = Document(text=doc_text, cursor_position=cursor_pos)

        completions = self._get_fuzzy_completions(self._get_completions(doc2,
                                                                        event,
                                                                        groups),
                                                  text)
        return completions

    def _parse_group_filters(self, text):
        filtered_groups = []
        rest_text = text
        if text.startswith('group='):
            filter_content = text.split(' ')[0]
            rest_text = ' '.join(text.split(' ')[1:])
            groups = filter_content.split('=')[1]
            filtered_groups = groups.split(',')
        return rest_text, filtered_groups

    def _get_completions(self, doc, event, filter_groups):
        word = doc.get_word_before_cursor().strip()
        snippets = self._snippets
        if filter_groups:
            snippets = _filter_by_group(self._snippets, filter_groups)
        for snippet in snippets:
            match = self._match(snippet, word)
            if match is None:
                continue
            yield Completion(match,
                             start_position=-len(word),
                             style='fg:white bg:black',
                             selected_style='bg:green')

    def _get_fuzzy_completions(self, completions, word):
        fuzzy_matches = []
        pat = '.*?'.join(map(re.escape, word))
        pat = '(?=({0}))'.format(pat)
        regex = re.compile(pat, re.IGNORECASE)
        for compl in completions:
            matches = list(regex.finditer(compl.text))
            if matches:
                # Prefer the match, closest to the left, then shortest.
                best = min(matches, key=lambda m: (m.start(), len(m.group(1))))
                fuzzy_matches.append(_FuzzyMatch(len(best.group(1)),
                                                 best.start(),
                                                 compl))

        def sort_key(fuzzy_match):
            " Sort by start position, then by the length of the match. "
            return fuzzy_match.start_pos, fuzzy_match.match_length

        fuzzy_matches = sorted(fuzzy_matches, key=sort_key)

        for match in fuzzy_matches:
            old_comp = match.completion
            start_pos = old_comp.start_position - len(word)
            display = self._get_display(match, word)
            style = old_comp.style
            selected_style = old_comp.selected_style
            completion = Completion(old_comp.text,
                                    display=display,
                                    start_position=start_pos,
                                    style=style,
                                    selected_style=selected_style)
            yield completion
