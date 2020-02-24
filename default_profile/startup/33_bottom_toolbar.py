"""Draw a toolbar for the shell using prompt_toolkit.

Takes into consideration whether Emacs mode or Vi mode is set
and adds :kbd:`F4` as a keybindings to toggle between each.

TODO: currently initialize a titlebar, an exit button and a few
other things that aren't utilized at all.

"""
import functools
import logging
import time
from datetime import date
from pathlib import Path
from shutil import get_terminal_size
from traceback import print_exc

from prompt_toolkit.enums import EditingMode

# from prompt_toolkit.formatted_text import FormattedText, to_formatted_text
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window, Float
from prompt_toolkit.layout.layout import Layout

# from prompt_toolkit.layout.processors import DisplayMultipleMouses
from prompt_toolkit.shortcuts import print_formatted_text, CompleteStyle
from prompt_toolkit.shortcuts.utils import print_container
from prompt_toolkit.styles import default_pygments_style
from prompt_toolkit.styles import Style, merge_styles, style
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.widgets import Frame, TextArea, Button
from prompt_toolkit.widgets.toolbars import FormattedTextToolbar

from pygments.token import Token
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from IPython.core.getipython import get_ipython
from IPython.terminal.ptutils import IPythonPTLexer

try:
    from gruvbox.gruvbox import GruvboxStyle
except ImportError:
    GruvboxStyle = None

logging.basicConfig()


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app


def exit_clicked():
    """Exit from the prompt_toolkit side of things."""
    get_app().exit(result=False, exception=EOFError)


def init_style():
    # Could set this to _ip.pt_app.style i suppose
    if GruvboxStyle is not None:
        bt_style = GruvboxStyle()
        ours = style_from_pygments_cls(bt_style)
        return merge_styles([ours, default_pygments_style()])


def show_header():
    # TODO: Should replace that text with somethin else
    text_area = TextArea(get_ipython().banner, style="#ebdbb2")
    return Frame(text_area)


class LineCounter:
    """Simple counter inspired by Doug Hellman. Could set it to sys.displayhook.

    :URL: https://pymotw.com/3/sys/interpreter.html

    """

    def __init__(self):
        self.count = 0
        self.time = strftime("%H:%M:%S")

    def __call__(self):
        """Yes!!! This now behaves as expected."""
        self.count += 1
        return "(< In[{:3d}]: Time:{}  )".format(self.count, self.time)


class BottomToolbar:
    """Display the current input mode.

    As the bottom_toolbar property exists in both a prompt_toolkit PromptSession
    and Application, both are accessible from the `session` and `pt_app`
    attributes.

    Defines a method :meth:`rerender` and calls it whenever the instance is called
    via ``__call__``.
    """

    def __init__(self, app, *args, **kwargs):
        """Require an 'app' for initialization.

        This will eliminate all IPython code out of this class and make things
        a little more modular for the tests.
        """
        self.shell = get_ipython()
        self.app = app
        # self.unfinished_toolbar = self.rerender()
        if self.app is None:
            logging.warning("BottomToolbar app is None.")
        self.PythonLexer = PythonLexer()
        self.Formatter = TerminalTrueColorFormatter()

    # @property
    # def app(self):
    #     # TODO: Be more consistent and check multiple versions of pt as done in other files
    #     return self.shell.pt_app.app

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
        return f"{self.rerender()!r}"

    def __call__(self):
        return f"{self.rerender()}"

    def terminal_width(self):
        """Returns `shutil.get_terminal_size.columns`."""
        return get_terminal_size().columns

    def __len__(self):
        """The length of the text we display."""
        return len(self.rerender())

    def full_width(self):
        """Bool indicating bottom toolbar == shutil.get_terminal_size().columns."""
        return len(self) == self.terminal_width()

    def rerender(self):
        """Render the toolbar at the bottom for prompt_toolkit.

        .. warning::
            Simple reminder about the difference between running an
            expression and returning one.
            If you accidentally forget the `return` keyword, nothing will
            display.
            That's all.
        """
        if self.is_vi_mode:
            return self._render_vi()
        else:
            return self._render_emacs()

    def _render_vi(self):
        current_vi_mode = self.app.vi_state.input_mode
        # temp_toolbar = f" [F4] Vi: {current_vi_mode!r}  {date.today()!r}"
        # toolbar = Frame(TextArea(temp_toolbar))
        # return toolbar.body

        # doing it this way only prints the words class:toolbar at the bottom
        # text = f" [F4] Vi: {current_vi_mode!r}  {date.today()!r}"
        # toolbar = [('class:toolbar', ' %s ' % text)]
        toolbar = f" [F4] Vi: {current_vi_mode!r} -- cwd: {Path.cwd().stem!r} Clock: {time.ctime()!r}"
        return toolbar

    def _render_emacs(self):
        # return [(Token.Generic.Heading, "[F4] Emacs: "),
        #         (Token.Generic.Prompt, f"{Path.cwd()} {date.today()}")]
        # temp_toolbar = f" [F4] Emacs: {Path.cwd()!r} {date.today()!a}"
        # toolbar = Frame(TextArea(temp_toolbar))
        # return toolbar.body
        toolbar = f" [F4] Emacs: {Path.cwd()!r} {date.today()!a}"
        return toolbar


def add_toolbar(toolbar=None):
    """Get the running IPython instance and add 'bottom_toolbar'."""
    _ip = get_ipython()
    if _ip is not None:
        if hasattr(_ip, "pt_app"):
            _ip.pt_app.bottom_toolbar = toolbar


if __name__ == "__main__":
    bottom_text = BottomToolbar(get_app())

    partial_window = Window(FormattedTextControl(bottom_text), width=10, height=2)

    logging.debug(print_container(partial_window))
    # Do frames not return container objects? Because this line is raisin an error?
    # bottom_float = Float(Frame(partial_window, style="bg:#282828 #ffffff"), bottom=0)
    # print_container(bottom_float)
    bottom_toolbar = FormattedTextToolbar(bottom_text)
    add_toolbar(bottom_text)
    print_container(show_header())
