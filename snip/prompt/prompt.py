from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit.lexers import DynamicLexer
from prompt_toolkit.shortcuts import prompt, PromptSession
from prompt_toolkit.shortcuts.prompt import _split_multiline_prompt, CompleteStyle
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.menus import _get_menu_item_fragments
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


def select_snippet(snippets):
    snippet_completer = SnippetCompleter(snippets)
    session = SplitPromptSession()
    desc = session.prompt(HTML('<b>> </b>'), completer=snippet_completer)
    return desc


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
                    auto_suggest_bindings,
                    ConditionalKeyBindings(open_in_editor_bindings,
                        dyncond('enable_open_in_editor') &
                        has_focus(DEFAULT_BUFFER)),
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


class SnippetCompleter(Completer):
    def __init__(self, descriptions):
        super(SnippetCompleter).__init__()
        self._descriptions = descriptions

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for desc in self._descriptions:
            if desc.startswith(word):
                yield Completion(desc,
                                 start_position=-len(word),
                                 style='fg:white bg:black',
                                 selected_style='fg:green bg:#000005')
