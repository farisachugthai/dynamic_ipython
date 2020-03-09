"""Configure prompt_toolkit effectively within a running IPython instance.

Summary
-------
Provides utilities functions and classes to work with both `prompt_toolkit`
and `IPython`. The APIs of both libraries can be individually quite
overwhelming, and the combination and interaction of the 2 can prove difficult
to stay on top of.

The `Helpers` class defined here gives a useful reference as to the
relationship between a number of the intertwined classes in a running
`PromptSession`.

Notes
-----
Of use might be.:

    get_ipython().pt_app.layout

An object that contains the default_buffer, `DEFAULT_BUFFER`, a reference
to a container `HSplit` and a few other things possibly worth exploring.

"""
from reprlib import repr
import sys

import prompt_toolkit
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition, is_searching
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import merge_key_bindings
from prompt_toolkit.key_binding.bindings import search
from prompt_toolkit.key_binding.bindings.auto_suggest import load_auto_suggest_bindings
from prompt_toolkit.key_binding.bindings.vi import (
    load_vi_bindings,
    load_vi_search_bindings,
)
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.styles import Style
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.widgets.toolbars import SearchToolbar
from prompt_toolkit.layout.processors import (
    ConditionalProcessor,
    DisplayMultipleCursors,
    HighlightSearchProcessor,
    HighlightIncrementalSearchProcessor,
    HighlightSelectionProcessor,
    HighlightMatchingBracketProcessor,
    DisplayMultipleCursors,
)
from IPython.core.getipython import get_ipython

from pygments.styles.inkpot import InkPotStyle


DEDENT_TOKENS = frozenset(["raise", "return", "pass", "break", "continue"])


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app


def get_session():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app


class Helpers:
    """A class that attempt enumerating the hierarchy of classes in prompt_toolkit."""

    def __init__(self):
        """Define the shell, PromptSession and Application."""
        self.shell = get_ipython()
        self.pt_app = get_app()
        self.session = get_session()

    def __repr__(self):
        return f"{self.__class__.__name__} with app at {self.pt_app}"

    def __sizeof__(self):
        # Unfortunately I've added so much to this class that it might be necessary to check
        # how big ano object is now
        return object.__sizeof__(self) + sum(
            sys.getsizeof(v) for v in self.__dict__.values()
        )

    @property
    def app_kb(self):
        """Application instance keybindings.

        NOT the same as 'session_kb'.

        In [103]: pt.pt_app_kb == pt.session_kb
        Out[103]: False
        """
        return self.pt_app.key_bindings

    @property
    def session_kb(self):
        return self.session.key_bindings

    @property
    def app_layout(self):
        """The same as session_layout *thank god*.

        In [102]: pt.app_layout == pt.session_layout
        Out[102]: True
        """
        return self.pt_app.layout

    @property
    def session_layout(self):
        return self.session.layout

    @property
    def layout(self):
        return self.app_layout

    @property
    def app_style(self):
        """Of course it's not the same as the session_style.

        ::

            In [108]: pt.pt_app.style
            Out[108]: <prompt_toolkit.styles.base.DynamicStyle at 0x7f164da54f40>

            In [109]: pt.session.style
            Out[109]: <prompt_toolkit.styles.base.DynamicStyle at 0x7f1658a90a30>
        """
        return self.pt_app.style

    @property
    def editing_mode(self):
        """Thankfully the same on a PromptSession and Application.

        In [5]: _ip.pt_app.editing_mode
        Out[5]: <EditingMode.VI: 'VI'>

        In [6]: _ip.pt_app.app.editing_mode
        Out[6]: <EditingMode.VI: 'VI'>
        """
        return self.session.editing_mode

    @property
    def session_style(self):
        return self.session.style

    @property
    def current_buffer(self):
        """Current buffer as returned by the layout property."""
        return self.layout.current_buffer

    @property
    def current_buffer_app(self):
        """Current buffer a returned by the App. Doesn't exist on the PromptSession."""
        return self.session.current_buffer

    # todo:
    # In [3]: _ip.pt_app.validator

    # In [4]: _ip.pt_app.app.validator
    # AttributeError: 'Application' object has no attribute 'validator'

    @property
    def current_container(self):
        """Return the container attr of the layout.

        Typically will return the HSplit defining the layout of the app.
        """
        return self.layout.container

    @property
    def current_container_children(self):
        """Return a list of the current container children.

        I genuinely don't think I expected it to be so big.

        .. admonition:: HSplit.children is a lie.

            Use HSplit._all_children

        """
        return self.current_container._all_children

    @property
    def current_control(self):
        """Return the layout's current control. Typically a BufferControl."""
        return self.layout.current_control

    @property
    def current_document(self):
        """The current buffer's document."""
        return self.current_buffer.document

    @property
    def current_buffer_texts(self):
        """Return the 'text' attr of the current buffer as a string."""
        return self.current_buffer.text

    @property
    def current_document_text(self):
        """Return the 'lines' attr of the current document as a list."""
        return self.current_document.lines

    @property
    def current_window(self):
        return self.layout.current_window

    @property
    def current_content(self):
        """The 'content' attribute of a `Window` returns a UIControl instance.

        In this specific case, it returns a BufferControl.
        """
        return self.current_window.content

    @property
    def content_is_control(self):
        """Is the `Window` content the control returned by the layout?"""
        return self.current_content is self.current_control

    @property
    def session_validator(self):
        """The validator instance on the PromptSession.

        Notes
        -----
        Not only do we not have this attribute on the App, it's not bound to
        anything by default in IPython!
        """
        return self.session.validator

    # Doesn't actually exist!
    # @property
    # def app_validator(self):
    #     return self.pt_app.validator

    def validate_validators(self):
        # who watches the watchmen?
        print("Session validator: {}".format(self.session_validator))
        print(isinstance(self.session_validator, prompt_toolkit.validator.Validator))
        print("Is the app validator the same as the session validator?")
        print(self.app_validator is self.session_validator)

    def all_controls(self):
        return list(self.layout.find_all_controls())

    @property
    def app_renderer(self):
        """Note that session doesn't have this attribute."""
        return self.pt_app.renderer

    @property
    def renderer_output(self):
        """The output attribute from the `prompt_toolkit.renderer.Renderer`.

        Examples
        --------
        ::

            In [9]: h = Helpers()

            In [10]: h.session.output
            Out[10]: <prompt_toolkit.output.windows10.Windows10_Output at 0x240ff55b460>

            In [11]: h.pt_app.output
            Out[11]: <prompt_toolkit.output.windows10.Windows10_Output at 0x240ff55b460>

            In [12]: h.session.input
            Out[12]: <prompt_toolkit.input.win32.Win32Input at 0x240ff722050>

            In [13]: h.pt_app.input
            Out[13]: <prompt_toolkit.input.win32.Win32Input at 0x240ff722050>

        """
        return self.app_renderer.output

    def current_buffer_lines(self):
        """Effectively a full history of every command I've run across sessions.

        This is crazy to look at and I don't know where it's storing this
        persistent info.

        Returns
        -------
        _working_lines : lines

        """
        return self.current_buffer._working_lines

    def app_context(self):
        """What is this?

        Behaves similarly to a dict but won't display values.::

            [ins] In [165]: _ip.pt_app.app.context
            Out[165]: <Context at 0x7877b7d880>

            [ins] In [166]: _ip.pt_app.app.context.items()
            Out[166]: <items at 0x7877ac00f0>

            [ins] In [167]: _ip.pt_app.app.context.keys()
            Out[167]: <keys at 0x7877b46e00>

            [ins] In [168]: print_formatted_text(_ip.pt_app.app.context)
            <Context object at 0x787791c380>

        """
        return self.pt_app.context


def all_processors_for_searching():
    r"""Return a list of `prompt_toolkit.layout.processor.Processor`\'s."""
    return [
        ConditionalProcessor(HighlightSearchProcessor(), ~is_searching),
        HighlightIncrementalSearchProcessor(),
        HighlightSelectionProcessor(),
        HighlightMatchingBracketProcessor(),
        DisplayMultipleCursors(),
    ]


def search_layout():
    """Generate a `Layout` with a `SearchToolbar` and keybindings.

    Notes
    ------
    Windows require their `content` arguments to have a method `reset`.

    """
    all_input_processors = all_processors_for_searching()
    search_toolbar = SearchToolbar("Search Toolbar", vi_mode=True)
    control = BufferControl(
        Buffer(document=Document(), read_only=True),
        search_buffer_control=search_toolbar.control,
        preview_search=True,
        include_default_input_processors=False,
        input_processors=all_processors_for_searching(),
    )
    style = style_from_pygments_cls(InkPotStyle)
    # Apparently theres something wrong with the style other put it in the
    # HSplit constructor
    buf_container = Window(control, style=style)
    search_container = Window(search_toolbar, style=style)
    container = HSplit([buf_container, search_container])
    return container


def create_searching_keybindings():

    kb = KeyBindings()

    @kb.add("q")
    def _(event):
        event.app.exit()

    @Condition
    def search_buffer_is_empty():
        """Returns True when the search buffer is empty."""
        return get_app().current_buffer.text == ""

    kb.add("/")(search.start_forward_incremental_search)
    kb.add("?")(search.start_reverse_incremental_search)
    kb.add("enter", filter=is_searching)(search.accept_search)
    kb.add("c-c")(search.abort_search)
    kb.add("backspace", filter=search_buffer_is_empty)(search.abort_search)

    @kb.add("n", filter=~is_searching)
    def _(event):
        search_state = get_app().current_search_state
        current_buffer = get_app().current_buffer

        cursor_position = current_buffer.get_search_position(
            search_state, include_current_position=False
        )
        current_buffer.cursor_position = cursor_position

    @kb.add("N", filter=~is_searching)
    def _(event):
        search_state = get_app().current_search_state
        current_buffer = get_app().current_buffer

        cursor_position = current_buffer.get_search_position(
            ~search_state, include_current_position=False
        )
        current_buffer.cursor_position = cursor_position

    return kb


if __name__ == "__main__":
    pt_helper = Helpers()
    # container_search = search_layout()

    # Honestly I'm wary to do this but let's go for it
    if get_ipython() is not None:
        all_kb = merge_key_bindings(
            [
                get_ipython().pt_app.app.key_bindings,
                load_vi_bindings(),
                load_vi_search_bindings(),
                load_auto_suggest_bindings(),  # these stopped getting added when i did this
            ]
        )
        get_ipython().pt_app.app.key_bindings = all_kb
        get_ipython().pt_app.app.key_bindings._update_cache()
