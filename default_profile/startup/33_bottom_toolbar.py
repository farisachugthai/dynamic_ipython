"""Draw a toolbar for the shell using prompt_toolkit.

Takes into consideration whether Emacs mode or Vi mode is set
and adds :kbd:`F4` as a keybindings to toggle between each.

"""
import functools
from datetime import date
from pathlib import Path
from shutil import get_terminal_size
from traceback import print_exc

from prompt_toolkit import ANSI, HTML
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.shortcuts import print_formatted_text, CompleteStyle
from prompt_toolkit.styles import default_pygments_style

from prompt_toolkit.styles import Style, merge_styles, style
from prompt_toolkit.styles.pygments import (
    style_from_pygments_cls,
    style_from_pygments_dict,
)

from pygments.token import Token
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from IPython.core.getipython import get_ipython

try:
    from gruvbox.gruvbox import Gruvbox
except ImportError:
    Gruvbox = None

completion_displays_to_styles = {
    "multi": CompleteStyle.MULTI_COLUMN,
    "single": CompleteStyle.COLUMN,
    "readline": CompleteStyle.READLINE_LIKE,
    "none": None,
}


def init_style():
    # Could set this to _ip.pt_app.style i suppose
    if Gruvbox is not None:
        bt_style = Gruvbox()
        return style_from_pygments_dict(bt_style.style_rules)


def override_style(style_overrides):
    style = init_style()
    if not hasattr(style_overrides):
        raise TypeError
    style_overrides = Style.from_dict(style_overrides)
    try:
        return merge_styles([style, style_overrides])
    except (AttributeError, TypeError, ValueError):
        print_exc()


def merged_styles(overrides=None):
    base = init_style()

    return merge_styles([base, overrides, default_pygments_style()])


class BottomToolbar:
    """Display the current input mode.

    As the bottom_toolbar property exists in both a prompt_toolkit PromptSession
    and Application, both are accessible from the `session` and `pt_app`
    attributes.

    Defines a method :meth:`rerender` and calls it whenever the instance is called
    via ``__call__``.
    """

    def __init__(self, *args, **kwargs):
        self.shell = get_ipython()
        self.unfinished_toolbar = self.rerender()
        self.PythonLexer = PythonLexer()
        self.Formatter = TerminalTrueColorFormatter()

    @property
    def session(self):
        return self.shell.pt_app

    @property
    def app(self):
        # TODO: Be more consistent and check multiple versions of pt as done in other files
        return self.shell.pt_app.app

    @property
    def is_vi_mode(self):
        if self.app.editing_mode == EditingMode.VI:
            return True
        else:
            return False

    def __str__(self):
        return f"<{self.__class__.__name__!s}:>"

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
        # TODO:
        # add more styling:
        # [('class:toolbar', ' [F4] %s ' % text)]
        current_vi_mode = self.app.vi_state.input_mode
        toolbar = f" [F4] Vi: {current_vi_mode!r}  {date.today()!r}"
        # toolbar.append(style=default_pygments_style())
        return toolbar

    def _render_emacs(self):
        # return [(Token.Generic.Heading, "[F4] Emacs: "),
        #         (Token.Generic.Prompt, f"{Path.cwd()} {date.today()}")]
        # Nope! str and _Token can't be concatenated and this'll not only freeze
        # the running session but the terminal itself
        toolbar = f" [F4] Emacs: {Path.cwd()!r} {date.today()!a}"
        # really upset this didn't work `{date.today():>{len(self)}}"
        # goddamn neither did that
        # return "{} {:>150}".format(toolbar, date.today())
        return toolbar


def add_toolbar(toolbar=None):
    """Get the running IPython instance and add 'bottom_toolbar'."""
    _ip = get_ipython()
    if hasattr(_ip, "pt_app"):
        _ip.pt_app.bottom_toolbar = toolbar


# Don't uncomment! This fucks up the keybindings so that the only way a line
# executes is if you use C-r to get into a search then hit something to regain
# focus and then hit enter.
# Unbelievable. It wasn't this block. it was load_key_bindings()?????
if __name__ == "__main__":
    if get_ipython() is not None:
        add_toolbar(BottomToolbar)
