"""Configure prompt_toolkit effectively within a running IPython instance.

Summary
-------

Create classes used to enhance the prompt_toolkit objects
bound to the running IPython interpreter.

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
import functools
import sys

import jedi
import prompt_toolkit
from IPython.core.getipython import get_ipython
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
# from prompt_toolkit.keys import Keys
# from prompt_toolkit.key_binding import merge_key_bindings
from prompt_toolkit.filters import is_searching, ViInsertMode
from prompt_toolkit.key_binding.bindings import search
from prompt_toolkit.key_binding.key_bindings import (
    KeyBindings, ConditionalKeyBindings, _MergedKeyBindings
)
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.processors import (
    ConditionalProcessor,
    HighlightSearchProcessor,
    HighlightIncrementalSearchProcessor,
    HighlightSelectionProcessor,
    HighlightMatchingBracketProcessor,
    DisplayMultipleCursors,
)
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.validation import (
    ConditionalValidator,
    ThreadedValidator,
    DummyValidator,
)
from prompt_toolkit.widgets.toolbars import SearchToolbar

try:
    from gruvbox import GruvboxStyle
except ImportError:
    from pygments.styles.inkpot import InkPotStyle
    pygments_style = InkPotStyle
else:
    pygments_style = GruvboxStyle


DEDENT_TOKENS = frozenset(["raise", "return", "pass", "break", "continue"])


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app


def get_session():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app


def get_jedi_interpreter(document):
    # Copied from ptpython.utils
    try:
        return jedi.Interpreter(
            document.text,
            column=document.cursor_position_col,
            line=document.cursor_position_row + 1,
            path="input-text",
            namespaces=[locals, globals],
        )
    except ValueError:
        # Invalid cursor position.
        # ValueError('`column` parameter is not in a valid range.')
        return None
    except AttributeError:
        # Workaround for #65: https://github.com/jonathanslenders/python-prompt-toolkit/issues/65
        # See also: https://github.com/davidhalter/jedi/issues/508
        return None
    except IndexError:
        # Workaround Jedi issue #514: for https://github.com/davidhalter/jedi/issues/514
        return None
    except KeyError:
        # Workaroud for a crash when the input is "u'", the start of a unicode string.
        return None
    # except Exception:
    # Workaround for: https://github.com/jonathanslenders/ptpython/issues/91
    # return None


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
        # noinspection PyProtectedMember
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
        print(
            f"Session validator: {self.session_validator}."
            "Checking if the session validator is a prompt_toolkit.validator.Validator."
        )
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
        # noinspection PyProtectedMember
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
        input_processors=all_input_processors,
    )
    style = style_from_pygments_cls(pygments_style)
    # Apparently theres something wrong with the style other put it in the
    # HSplit constructor
    buf_container = Window(control, style=style)
    search_container = Window(search_toolbar, style=style)
    container = HSplit([buf_container, search_container])
    return container


def create_searching_keybindings():
    kb = KeyBindings()
    # These get referenced more than once so keep them up here
    search_state = get_app().current_search_state
    current_buffer = get_app().current_buffer

    @kb.add("q")
    def _(event):
        event.app.exit()

    # @Condition
    # def search_buffer_is_empty():
    #     """Returns True when the search buffer is empty."""
    #     return get_app().current_buffer.text == ""

    kb.add("/")(search.start_forward_incremental_search)
    kb.add("?")(search.start_reverse_incremental_search)
    kb.add("enter")(search.accept_search)
    kb.add("c-c")(search.abort_search)
    kb.add("backspace")(search.abort_search)

    @kb.add("n")
    def repeat_search(event):
        cursor_position = current_buffer.get_search_position(
            search_state, include_current_position=False
        )
        current_buffer.cursor_position = cursor_position

    @kb.add("N")
    def repeat_search_backwards(event):
        cursor_position = current_buffer.get_search_position(
            ~search_state, include_current_position=False
        )
        current_buffer.cursor_position = cursor_position

    return ConditionalKeyBindings(kb, filter=is_searching)


class ConditionalCallable(ConditionalValidator):
    def __init__(self, validator, **kwargs):
        if kwargs:
            if "document" in kwargs:
                self.document = kwargs.pop("document")

        super().__init__(validator, **kwargs)

    # def validate(self, document, filter=None, *args, **kwargs):
    #     """Only abstract method is validate. Fuckin' ConditionalValidator doesn't define this though."""
    #     self.validator.validate(document)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.validator}"

    # NOPE. We raise an error because 'validator type: str doesn't have a validate method.
    # So this class defines validation in terms of `__call__` at some point.
    # def __call__(self):
    # """Because it's annoying having to pass the document just to see it."""
    # return self.__repr__()

    def __call__(self, document=None):
        if document is None:
            document = get_ipython().pt_app.app.current_buffer.document
        return self.validate(document)


def _conditional_validator(validator, document):
    return ConditionalCallable(validator, document=document, filter=ViInsertMode())


def pt_validator() -> prompt_toolkit.validation.Validator:
    validator = ThreadedValidator(
        _conditional_validator(
            DummyValidator(), get_ipython().pt_app.app.current_buffer.document
        )
    )
    return validator


def user_overrides(f, overrides=None, *args, **kwargs):
    """Decorator that allows a user to fill in the remainder of a functools.partial."""
    # problematically i don't really know how to do this.

    @functools.wraps
    def _():
        return f(overrides)

    return f(*args, **kwargs)


def initialize_prompt_toolkit(prompt=None):
    # make these imports local because shits gonna run so slow otherwise
    from default_profile.startup.lexer import get_lexer
    # from default_profile.startup.completions import create_pt_completers
    # from default_profile.startup.clipboard import UsefulClipboard
    from prompt_toolkit.clipboard.base import DynamicClipboard
    from prompt_toolkit.clipboard.in_memory import InMemoryClipboard
    from prompt_toolkit.key_binding.defaults import load_key_bindings

    if prompt is None:
        prompt = 'YourPTApp:'
    from prompt_toolkit.output import ColorDepth
    partial_session = functools.partial(prompt_toolkit.shortcuts.PromptSession(
        message=prompt,
        vi_mode=True,
        lexer=get_lexer(),
        key_bindings=load_key_bindings(),
        enable_open_in_editor=True,
        enable_history_search=True,
        enable_system_prompt=True,
        enable_suspend=True,
        color_depth=ColorDepth.TRUE_COLOR,
        clipboard=DynamicClipboard(InMemoryClipboard()),
        validator=pt_validator(),
        # TODO: style
        # include_default_pygments_style
        # history
        # and then eventually layout
    ))
    return partial_session


def determine_which_pt_attribute():
    _ip = get_ipython()
    # IPython < 7.0
    if hasattr(_ip, "pt_cli"):
        return _ip.pt_cli.application.key_bindings_registry
    # IPython >= 7.0
    elif hasattr(_ip, "pt_app"):
        # Here's one that might blow your mind.
        if _ip.pt_app is None:
            # also happens in pydevd in pycharm. we gotta fix this though.
            # ran into this while running pytest.
            # If you start IPython from something like pytest i guess it starts
            # the machinery with a few parts missing...I don't know.
            initialize_prompt_toolkit()
        ret = _ip.pt_app.app.key_bindings
        if isinstance(ret, _MergedKeyBindings):
            # returning _bindings2 returns None omfg
            return ret.bindings
        elif isinstance(ret, KeyBindings):
            return ret.bindings
        else:
            raise TypeError

    else:
        try:
            from ipykernel.zmqshell import ZMQInteractiveShell
        except (ImportError, ModuleNotFoundError):
            return
        else:
            # Jupyter QTConsole
            if isinstance(_ip, ZMQInteractiveShell):
                return


if __name__ == "__main__":
    try:
        pt_helper = Helpers()
    except Exception as e:  # noqa
        print(e)

    pt = determine_which_pt_attribute()
    get_ipython().pt_app.validator = pt_validator()
