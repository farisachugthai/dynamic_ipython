#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Draw a toolbar for the shell using prompt_toolkit.

Takes into consideration whether Emacs mode or Vi mode is set
and adds :kbd:`F4` as a keybindings to toggle between each.

TODO: currently initialize a titlebar, an exit button and a few
other things that aren't utilized at all.

"""
import sys
import textwrap
import time
from datetime import date
from pathlib import Path
from shutil import get_terminal_size
from typing import Dict, List, Any, AnyStr

import prompt_toolkit
from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShell
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import (
    PygmentsTokens,
    to_formatted_text,
)
from prompt_toolkit.shortcuts.utils import print_container
from prompt_toolkit.styles import default_pygments_style, style_from_pygments_cls
from prompt_toolkit.styles import merge_styles
from prompt_toolkit.widgets import Frame, TextArea
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.python import PythonLexer
from pygments.token import Token

try:
    from gruvbox import GruvboxStyle
except ImportError:
    # actually we can't do this. he requires that styles have an invalidationhash

    from pygments.styles.inkpot import InkPotStyle

    # pygments_style = default_pygments_style()
    pygments_style = InkPotStyle
else:
    pygments_style = GruvboxStyle


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app


def exit_clicked():
    """Exit from the prompt_toolkit side of things."""
    get_app().exit(result=False, exception=EOFError)


def init_style():
    """Merges the styles from default_pygments_style and the previously imported `pygments_style`."""
    return merge_styles(
        [style_from_pygments_cls(pygments_style), default_pygments_style()]
    )


def show_header(header_text: AnyStr = None) -> prompt_toolkit.widgets.Frame:
    if header_text is None:
        header_text = textwrap.dedent(
            "Press Control-Y to paste from the system _clipboard.\n"
            "Press Control-Space or Control-@ to enter selection mode.\n"
            "Press Control-W to cut to _clipboard.\n"
        )
    text_area = TextArea(header_text, style="#ebdbb2")
    return Frame(text_area)


def terminal_width():
    """Returns `shutil.get_terminal_size.columns`."""
    return get_terminal_size().columns


class LineCounter:
    """Simple counter inspired by Doug Hellman. Could set it to sys.displayhook.

    :URL: https://pymotw.com/3/sys/interpreter.html
    """

    def __init__(self):
        self.count = 0
        self.executable = sys.prefix

    def display(self):
        self.count += 1
        ret = [
            Token.String.Subheading,
            f"< In[{self.count:3d}]:",
            [Token.Literal, f"Time:{self.time}"],
        ]
        return ret

    def __call__(self):
        """Yes!!! This now behaves as expected."""
        return self.display()

    def __repr__(self):
        return f"<{self.__class__.__name__}:> {self.__call__}"

    @property
    def time(self):
        return time.strftime("%H:%M:%S")

    def __pt_formatted_text__(self):
        """A list of ``(style, text)`` tuples.

        (In some situations, this can also be ``(style, text, mouse_handler)``
        tuples.)
        """
        return self.display()


class BottomToolbar:
    """Display the current input mode.

    As the bottom_toolbar property exists in both a prompt_toolkit
    PromptSession and Application, both are accessible from the `session`
    and `pt_app` attributes.

    Defines a method :meth:`rerender` and calls it whenever the instance
    is called via ``__call__``.

    """

    shell: InteractiveShell

    # are you allowed to doctest fstrings

    def __init__(
        self, _style: prompt_toolkit.styles.Style = None, *args: List, **kwargs: Dict
    ) -> Any:
        """Require an 'app' for initialization.

        This will eliminate all IPython code out of this class and make things
        a little more modular for the tests.
        """
        self.shell = get_ipython()
        self.app = get_app()
        self.PythonLexer = PythonLexer()
        self.Formatter = TerminalTrueColorFormatter()
        self._style = _style if _style is not None else self.app.style

    @property
    def session(self):
        return self.shell.pt_app

    @property
    def layout(self):
        return self.shell.pt_app.layout

    @property
    def is_vi_mode(self):
        if self.app.editing_mode == EditingMode.VI:
            return True
        else:
            return False

    def __str__(self):
        return f"<{self.__class__.__name__!s}:>"

    def __iter__(self):
        for i in self.rerender():
            yield i

    def __repr__(self):
        return f"<{self.__class__.__name__!r}:>"

    def __call__(self):
        return f"{self.rerender()}"

    @property
    def style(self):
        return self._style

    @style.setter
    def reset_style(self, new_style):
        # do these function names even show up in `dir`?
        self._style = new_style

    def __len__(self):
        """The length of the text we display."""
        return len(self.rerender())

    def full_width(self):
        """Bool indicating bottom toolbar == shutil.get_terminal_size().columns."""
        return len(self) == terminal_width()

    def rerender(self):
        """Render the toolbar at the bottom for prompt_toolkit.

        .. warning::
            Simple reminder about the difference between running an
            expression and returning one.
            If you accidentally forget the `return` keyword, nothing will
            display. That's all.

        """
        if self.is_vi_mode:
            toolbar = PygmentsTokens(self._render_vi())
        else:
            toolbar = PygmentsTokens(self._render_emacs())
        return to_formatted_text(toolbar)

    def _render_vi(self):
        current_vi_mode = self.app.vi_state.input_mode
        _toolbar = [
            (Token.Keyword, f"[F4] {self.app.editing_mode!r}"),
            (Token.String.Heading, f"{current_vi_mode!r}"),
            (Token.Literal.String.Double, f"cwd: {Path.cwd().stem!r}"),
            (Token.Number.Integer, f"Clock: {time.ctime()!r}"),
        ]
        # how do i fill all this dead space?
        # remaining_space = terminal_width() - len(self)
        # _toolbar.append((Token.Operator, remaining_space * " "))
        # This crashes in a seemingly random spot and the whole interpreter
        # dies
        return _toolbar

    def _render_emacs(self):
        toolbar = f" [F4] {self.app.editing_mode}: {Path.cwd()!r} {date.today()!a}"
        return toolbar

    def __pt_formatted_text__(self):
        """A list of ``(style, text)`` tuples.

        (In some situations, this can also be ``(style, text, mouse_handler)``
        tuples.)
        """
        return self.rerender()


def add_toolbar(toolbar=None):
    """Get the running IPython instance and add 'bottom_toolbar'."""
    _ip = get_ipython()
    if _ip is not None:
        if hasattr(_ip, "pt_app"):
            if _ip.pt_app.bottom_toolbar is None:
                _ip.pt_app.bottom_toolbar = toolbar


if __name__ == "__main__":
    bottom_text = BottomToolbar(_style=pygments_style)
    add_toolbar(bottom_text)
    print_container(show_header())
    # TODO:
    #  partial_window = Window(width=60, height=3, style=pygments_style)
