#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up the lexer and highlighting processors for the app.

After importing either a Gruvbox pygments Style or InkPotStyle,
we `merge_styles` to return the final lexer.
"""
# TODO
# In [47]: _ip.pt_app.lexer.python_lexer.pygments_lexer
# Out[47]: <pygments.lexers.PythonLexer with {'stripnl': False, 'stripall': False, 'ensurenl': False}
import builtins
import inspect
import pprint
import pydoc
import shutil
import sys
import types

from traitlets.config import LoggingConfigurable
from traitlets.traitlets import Instance

import pygments
from pygments.lexer import Lexer
from pygments.lexers.python import PythonLexer
from pygments.token import Keyword, Name
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

from prompt_toolkit.formatted_text import FormattedText, PygmentsTokens
from prompt_toolkit.layout.containers import (
    HSplit,
    # VSplit,
    Window,
    WindowAlign,
    # for now
    # FloatContainer,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.lexers.pygments import PygmentsLexer
from prompt_toolkit.lexers.base import DynamicLexer, SimpleLexer
from prompt_toolkit.shortcuts.utils import print_container

from prompt_toolkit.styles import style_from_pygments_cls, default_pygments_style
from prompt_toolkit.styles.style import merge_styles  # , Style,
from prompt_toolkit.widgets import Button

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShellABC

# from IPython.lib.lexers import IPyLexer, IPythonTracebackLexer
# or IPython.terminal.ptutils.IPythonPTLexer

try:
    from gruvbox.ptgruvbox import Gruvbox
except ImportError:
    from pygments.styles.inkpot import InkPotStyle

    Gruvbox = InkPotStyle  # surprise!


def our_style():
    return merge_styles(
        [
            style_from_pygments_cls(Gruvbox),
            default_pygments_style(),
            #  Style.from_dict({'':''})
        ]
    )  # TODO
    return merge_styles(
        [style_from_pygments_cls(Gruvbox), default_pygments_style(), ]
    )  # TODO


def get_lexer():
    wrapped_lexer = PygmentsLexer(PythonLexer)
    return wrapped_lexer


def pygments_tokens():
    """A  list of Pygments style tokens. In case you need that."""
    return PygmentsTokens(Gruvbox.style_rules)


class IPythonConfigurableLexer(LoggingConfigurable):
    shell = Instance(InteractiveShellABC, allow_none=True)

    lexer = Instance(Lexer, help="Instance that lexs documents.", allow_none=True).tag(
        config=True
    )

    # from pygments.lexer.Lexer
    #: Name of the lexer
    name = None

    #: Shortcuts for the lexer
    aliases = []

    #: File name globs
    filenames = []

    #: Secondary file name globs
    alias_filenames = []

    #: MIME types
    mimetypes = []

    #: Priority, should multiple lexers match and no content is provided
    priority = 0

    def __init__(self, shell=None, original_lexer=None, **kwargs):
        super().__init__(**kwargs)
        self.shell = shell
        if self.shell is None:
            self.shell = get_ipython()

        if self.shell is not None:
            self.original_lexer = self.shell.pt_app.lexer
            self.shell.configurables.append("DynamicAliasManager")
        else:
            self.original_lexer = None


class Colorizer:
    """Make the pygments function 'highlight' even easier to work with.

    Additionally utilize ``__slots__`` to conserve memory.
    """

    __slots__ = {
        # The original docstring for pylexer was raising an error in sphinx...
        "pylexer": "A PythonLexer from Pygments",
        "formatter": TerminalTrueColorFormatter.__doc__,
        # 'highlight': pygments.highlight.__doc__
    }

    def __init__(self, pylexer=None, formatter=None):
        if pylexer is None:
            self.pylexer = PythonLexer()
        if formatter is None:
            self.formatter = TerminalTrueColorFormatter()

    def __call__(self, code):
        return self.highlight(code)

    def highlight(self, code):
        return pygments.highlight(code, self.pylexer, self.formatter)

    def __repr__(self):
        return f"{self.__class__.__name__}"


class MyPythonLexer(PythonLexer):
    EXTRA_KEYWORDS = set("!")

    def get_tokens_unprocessed(self, text):
        for index, token, value in PythonLexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.EXTRA_KEYWORDS:
                yield index, Keyword.Pseudo, value
            else:
                yield index, token, value


def get_titlebar_text():
    """Return (style, text) tuples for startup."""
    return [
        ("class:title", "Hello World!"),
        ("class:title", " (Press <Exit> to quit.)"),
    ]


def generate_and_print_hsplit():
    """Generate a `prompt_toolkit.layout.container.HSplit`.

    Originally was in 33_bottom_toolbar but moved here so we can use the lexer.
    """
    root_container = HSplit(
        children=[
            Window(
                height=1,
                content=FormattedTextControl(get_titlebar_text),
                align=WindowAlign.CENTER,
                wrap_lines=True,
            ),
            Window(height=1, char="-", style="class:line"),
        ],
        # key_bindings=kb,
        # style=GruvboxStyle,
        style="underline #80a0ff",
    )
    print("\n")
    print_container(root_container)
    # Thisll probably be useful
    # from prompt_toolkit.mouse_events import MouseEvent, MouseEventType

    # float_container = FloatContainer(content=Window(...),
    #                        floats=[
    #                            Float(xcursor=True,
    #                                 ycursor=True,
    #                                 layout=CompletionMenu(...))
    #                        ])
    exit_button = Button("Exit", handler=exit_clicked)
    print_container(exit_button)

    return root_container


# Pretty printing
def pphighlight(o, *a, **kw):
    s = pprint.pformat(o, *a, **kw)
    try:
        sys.stdout.write(pygments.highlight(s, PythonLexer(), TerminalTrueColorFormatter()))
    except UnicodeError:
        sys.stdout.write(s)
        sys.stdout.write("\n")


def extra_displayhook():
    help_types = [
        types.BuiltinFunctionType,
        types.BuiltinMethodType,
        types.FunctionType,
        types.MethodType,
        types.ModuleType,
        type,
        # method_descriptor
        type(list.remove),
    ]
    if hasattr(types, "UnboundMethodType"):
        help_types.append(types.UnboundMethodType)
    help_types = tuple(help_types)

    def get_width():
        return shutil.get_terminal_size()[1]

    if hasattr(inspect, "getfullargspec"):
        getargspec = inspect.getfullargspec
    else:
        getargspec = inspect.getargspec

    def pprinthook(value):
        """Pretty print an object to sys.stdout and also save it in
        __builtin__.
        """

        if value is None:
            return

        if isinstance(value, help_types):
            reprstr = repr(value)
            try:
                if inspect.isfunction(value):
                    parts = reprstr.split(" ")
                    parts[1] += inspect.formatargspec(*getargspec(value))
                    reprstr = " ".join(parts)
                elif inspect.ismethod(value):
                    parts = reprstr[:-1].split(" ")
                    parts[2] += inspect.formatargspec(*getargspec(value))
                    reprstr = " ".join(parts) + ">"
            except TypeError:
                pass
            sys.stdout.write(reprstr)
            sys.stdout.write("\n")
            if getattr(value, "__doc__", None):
                sys.stdout.write("\n")
                sys.stdout.write(pydoc.getdoc(value))
                sys.stdout.write("\n")
        else:
            pphighlight(value, width=get_width() or 80)

    sys.displayhook = pprinthook
    return pprinthook


if __name__ == "__main__":
    # lexer = IPythonConfigurableLexer()
    # colorizer = Colorizer()
    # pt_lexer = get_lexer()

    generate_and_print_hsplit()
    lexer = MyPythonLexer()
    # if hasattr(get_ipython(), "pt_app.lexer"):
    #     get_ipython().pt_app.lexer = lexer

    # elif hasattr(get_ipython(), "pt_app.app.lexer"):
    #     get_ipython().pt_app.app.lexer = lexer
