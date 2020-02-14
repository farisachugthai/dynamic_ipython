"""Draw a toolbar for the shell using prompt_toolkit.

Takes into consideration whether Emacs mode or Vi mode is set
and adds :kbd:`F4` as a keybindings to toggle between each.

TODO: currently initialize a titlebar, an exit button and a few
other things that aren't utilized at all.

"""
import functools
from datetime import date
from pathlib import Path
from shutil import get_terminal_size
from traceback import print_exc

from prompt_toolkit import ANSI, HTML
# from prompt_toolkit.application.current import get_app

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, FloatContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout

from prompt_toolkit.shortcuts import print_formatted_text, CompleteStyle
from prompt_toolkit.shortcuts.utils import print_container

from prompt_toolkit.styles import default_pygments_style
from prompt_toolkit.styles import Style, merge_styles, style
from prompt_toolkit.styles.pygments import (
    style_from_pygments_cls,
    style_from_pygments_dict,
)

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


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app


def exit_clicked():
    get_app().exit()


def init_style():
    # Could set this to _ip.pt_app.style i suppose
    if GruvboxStyle is not None:
        bt_style = GruvboxStyle()
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

def merged_style_rules():
    """Originally was going to call this in `show_header` but it raises if you
    had it a list or a Style instance. It looks like it's only made to take 1
    style anyway."""
    return merged_styles().style_rules

def show_header():
    text_area = TextArea(get_ipython().banner, style='#ebdbb2')
    return Frame(text_area)


class LineCounter:
    """Really basic counter displayed inspired by Doug Hellman.

    :URL: https://pymotw.com/3/sys/interpreter.html

    Need to set this to the rprompt.
    """

    def __init__(self):
        self.count = 0
        self.time = strftime('%H:%M:%S')

    def __call__(self):
        """Yes!!! This now behaves as expected."""
        self.count += 1
        return '(< In[{:3d}]: Time:{}  )'.format(self.count, self.time)



def get_titlebar_text():
    return [
        ("class:title", "Hello World!"),
        ("class:title", " (Press [TODO] to quit.)"),
    ]


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
        # temp_toolbar = f" [F4] Vi: {current_vi_mode!r}  {date.today()!r}"
        # toolbar = Frame(TextArea(temp_toolbar))
        # return toolbar.body
        toolbar = f" [F4] Vi: {current_vi_mode!r}  {date.today()!r}"
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
    if hasattr(_ip, "pt_app"):
        _ip.pt_app.bottom_toolbar = toolbar


class Attempt2(BottomToolbar, FormattedTextToolbar):
    pass

class Attempt3(BottomToolbar):
    def __init__(self):
        super().__init__()

    def _rerender(self):
        self.rerender()

    def __call__(self):
        return f"{self.toolbar()}"

    def toolbar(self):
        tmp = self._rerender()
        fmt = FormattedText(tmp)
        return FormattedTextToolbar(fmt)

# Don't uncomment! This fucks up the keybindings so that the only way a line
# executes is if you use C-r to get into a search then hit something to regain
# focus and then hit enter.
# Unbelievable. It wasn't this block. it was load_key_bindings()?????
if __name__ == "__main__":
    if get_ipython() is not None:
        add_toolbar(BottomToolbar)

    completion_displays_to_styles = {
        "multi": CompleteStyle.MULTI_COLUMN,
        "single": CompleteStyle.COLUMN,
        "readline": CompleteStyle.READLINE_LIKE,
        "none": None,
    }


    exit_button = Button("Exit", handler=exit_clicked)

    print_container(show_header())

    kb = get_ipython().pt_app.app.key_bindings.bindings
    # Bind to IPython TODO:
    root_container = HSplit(children=[
        Window(height=1, content=FormattedTextControl(get_titlebar_text), align=WindowAlign.CENTER,),
        Window(height=1, char="-", style="class:line")],
        key_bindings=kb,
        # style=GruvboxStyle,
        )

    print('\n\n\n')
    print_container(root_container)
    # Thisll probably be useful
    # from prompt_toolkit.mouse_events import MouseEvent, MouseEventType

    # float_container = FloatContainer(content=Window(...),
    #                        floats=[
    #                            Float(xcursor=True,
    #                                 ycursor=True,
    #                                 layout=CompletionMenu(...))
    #                        ])


