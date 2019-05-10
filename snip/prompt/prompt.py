from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter, WordCompleter
from prompt_toolkit.completion.fuzzy_completer import _FuzzyMatch
from prompt_toolkit.lexers import DynamicLexer
from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import prompt, PromptSession
from prompt_toolkit.shortcuts.prompt import _split_multiline_prompt, CompleteStyle
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.menus import _get_menu_item_fragments
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.clipboard import DynamicClipboard
from prompt_toolkit.layout.controls import (
    BufferControl,
    FormattedTextControl,
    UIControl,
    UIContent
)
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.key_binding.bindings.auto_suggest import load_auto_suggest_bindings
from prompt_toolkit.key_binding.key_bindings import (
    ConditionalKeyBindings,
    DynamicKeyBindings,
    merge_key_bindings,
)
from prompt_toolkit.key_binding.bindings.open_in_editor import (
    load_open_in_editor_bindings,
)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import (
    ConditionalStyleTransformation,
    DynamicStyle,
    DynamicStyleTransformation,
    SwapLightAndDarkStyleTransformation,
    merge_style_transformations,
)
from prompt_toolkit.filters import has_focus, is_done, Condition
from prompt_toolkit.layout.processors import (
    AppendAutoSuggestion,
    ConditionalProcessor,
    DisplayMultipleCursors,
    DynamicProcessor,
    HighlightIncrementalSearchProcessor,
    HighlightSelectionProcessor,
    PasswordProcessor,
    merge_processors,
)

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
    if len(prefix) < 2 or prefix not in SnippetCompleter.CATEGORY_PREFIXES:
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

        # Create processors list.
        all_input_processors = [
            HighlightIncrementalSearchProcessor(),
            HighlightSelectionProcessor(),
            ConditionalProcessor(AppendAutoSuggestion(),
                                 has_focus(default_buffer) & ~is_done),
            ConditionalProcessor(PasswordProcessor(), dyncond('is_password')),
            DisplayMultipleCursors(),

            # Users can insert processors here.
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
            #height=3,
            dont_extend_height=True,
            get_line_prefix=partial(
                self._get_line_prefix, get_prompt_text_2=get_prompt_text_2),
            wrap_lines=dyncond('wrap_lines'))
        completion_window = Window(content=CompletionsWidgetControl(),
                style='')

        # Build the layout.
        layout = HSplit([
            prompt_window,
            default_buffer_window,
            completion_window
        ])

        return Layout(layout, default_buffer_window)

    def _create_application(self, editing_mode, erase_when_done):
        """
        Create the `Application` object.
        """
        dyncond = self._dyncond

        # Default key bindings.
        auto_suggest_bindings = load_auto_suggest_bindings()
        open_in_editor_bindings = load_open_in_editor_bindings()
        prompt_bindings = self._create_prompt_bindings()

        # Create application
        application = Application(
            layout=self.layout,
            full_screen=True,
            style=DynamicStyle(lambda: self.style),
            style_transformation=merge_style_transformations([
                DynamicStyleTransformation(lambda: self.style_transformation),
                ConditionalStyleTransformation(
                    SwapLightAndDarkStyleTransformation(),
                    dyncond('swap_light_and_dark_colors'),
                ),
            ]),
            include_default_pygments_style=dyncond('include_default_pygments_style'),
            clipboard=DynamicClipboard(lambda: self.clipboard),
            key_bindings=merge_key_bindings([
                merge_key_bindings([
                    prompt_bindings
                ]),
                DynamicKeyBindings(lambda: self.key_bindings),
            ]),
            mouse_support=dyncond('mouse_support'),
            editing_mode=editing_mode,
            erase_when_done=erase_when_done,
            reverse_vi_search_direction=True,
            color_depth=lambda: self.color_depth,

            # I/O.
            input=self.input,
            output=self.output)

        return application


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
            return _get_menu_item_fragments(completion, is_curr_completion, width)
        return UIContent(get_line, line_count=len(completions))


class SnippetCompleter(FuzzyCompleter):
    CATEGORY_PREFIXES = ['c:', 'n:', 'd:']
    def __init__(self, snippets):
        super(SnippetCompleter).__init__()
        self._snippets = snippets
        self._search_strings = []

    def get_completions(self, doc, event):
        prompt_content = doc.text_before_cursor
        word, prefix = _strip_prefix(prompt_content)
        stripped_word = word.strip()
        if not stripped_word:
            return []
        self._search_strings = self._get_snippet_search_strings(prefix.strip())
        offset = len(prefix)
        doc2 = Document(text=doc.text[offset:doc.cursor_position - len(word)],
                        cursor_position=doc.cursor_position - len(word) - offset)

        return self._get_fuzzy_completions(self._get_completions(doc2, event),
                                           stripped_word)

    def _get_completions(self, doc, event):
        word = doc.get_word_before_cursor()
        for search_string in self._search_strings:
            if search_string.startswith(word):
                yield Completion(search_string,
                                 start_position=-len(word),
                                 style='fg:white bg:black',
                                 selected_style='bg:green')

    def _get_snippet_search_strings(self, prefix):
        if prefix == 'c:':
            words = [snippet.content for snippet in self._snippets]
        elif prefix == 'n:':
            words = [snippet.name for snippet in self._snippets]
        elif prefix == 'd:':
            words = [snippet.description for snippet in self._snippets]
        else:
            words = [snippet.content for snippet in self._snippets]
        words = filter(lambda w: bool(w), words)
        return words

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
                fuzzy_matches.append(_FuzzyMatch(len(best.group(1)), best.start(), compl))

        def sort_key(fuzzy_match):
            " Sort by start position, then by the length of the match. "
            return fuzzy_match.start_pos, fuzzy_match.match_length

        fuzzy_matches = sorted(fuzzy_matches, key=sort_key)

        for match in fuzzy_matches:
            # Include these completions, but set the correct `display`
            # attribute and `start_position`.
            completion = match.completion
            completion.start_position = completion.start_position - len(word)
            completion.display = self._get_display(match, word)
            yield completion

