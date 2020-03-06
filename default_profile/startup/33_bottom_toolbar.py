"""Draw a toolbar for the shell using prompt_toolkit.

Takes into consideration whether Emacs mode or Vi mode is set
and adds :kbd:`F4` as a keybindings to toggle between each.

TODO: currently initialize a titlebar, an exit button and a few
other things that aren't utilized at all.

"""
import asyncio
import functools
import time
import textwrap
from datetime import date
from pathlib import Path
from shutil import get_terminal_size
from traceback import print_exc

from prompt_toolkit.enums import EditingMode

from prompt_toolkit.formatted_text import PygmentsTokens
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
    from gruvbox import GruvboxStyle
except ImportError:
    GruvboxStyle = None
    from pygments.styles.inkpot import InkPotStyle

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
    # Could set this to _ip.pt_app.style i suppose
    if GruvboxStyle is not None:
        bt_style = GruvboxStyle()
        ours = style_from_pygments_cls(bt_style)
        return merge_styles([ours, default_pygments_style()])
    else:
        return default_pygments_style()


def show_header(header_text=None):
    if header_text is None:
        header_text = textwrap.dedent(
            "Press Control-Y to paste from the system clipboard.\n"
            "Press Control-Space or Control-@ to enter selection mode.\n"
            "Press Control-W to cut to clipboard.\n"
        )
    # TODO: Should replace that text with somethin else
    # XXX: style errors

    # [ins] In [15]: edit 33_bottom_toolbar.py
    # Editing... done. Executing edited code...
    # ---------------------------------------------------------------------------
    # TypeError                                 Traceback (most recent call last)
    # ~/projects/dynamic_ipython/default_profile/startup/33_bottom_toolbar.py in <module>
    #     244     bottom_toolbar = FormattedTextToolbar(PygmentsTokens(bottom_text), style=style)
    #     245     add_toolbar(bottom_text)
    # --> 246     print_container(show_header())
    #         global print_container = <function print_container at 0x73eefc0670>
    #         global show_header = <function show_header at 0x73ec91c9d0>

    # ~/projects/dynamic_ipython/default_profile/startup/33_bottom_toolbar.py in show_header(header_text='Press Control-Y to paste from the system clipboa...ction mode.\nPress Control-W to cut to clipboard.\n')
    #      79         )
    #      80     # TODO: Should replace that text with somethin else
    # ---> 81     text_area = TextArea(header_text, style=style_from_pygments_cls(InkPotStyle))
    #         text_area = undefined
    #         global TextArea = <class 'prompt_toolkit.widgets.base.TextArea'>
    #         header_text = 'Press Control-Y to paste from the system clipboard.\nPress Control-Space or Control-@ to enter selection mode.\nPress Control-W to cut to clipboard.\n'
    #         global style = <prompt_toolkit.styles.style.Style object at 0x73eb333070>
    #         global style_from_pygments_cls = <function style_from_pygments_cls at 0x73ef4dbee0>
    #         global InkPotStyle = <class 'pygments.styles.inkpot.InkPotStyle'>
    #      82     # its legitimately insane to me that this raises.
    #      83     # TODO: Changes what a style is

    # ~/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/prompt_toolkit/widgets/base.py in __init__(self=<prompt_toolkit.widgets.base.TextArea object>, text='Press Control-Y to paste from the system clipboa...ction mode.\nPress Control-W to cut to clipboard.\n', multiline=True, password=False, lexer=None, auto_suggest=None, completer=None, complete_while_typing=True, accept_handler=None, history=None, focusable=True, focus_on_click=False, wrap_lines=True, read_only=False, width=None, height=None, dont_extend_height=False, dont_extend_width=False, line_numbers=False, get_line_prefix=None, scrollbar=False, style=<prompt_toolkit.styles.style.Style object>, search_field=None, preview_search=True, prompt='', input_processors=[])
    #     252             right_margins = []
    #     253
    # --> 254         style = "class:text-area " + style
    #         style = <prompt_toolkit.styles.style.Style object at 0x73eb333130>
    #     255
    #     256         self.window = Window(

    # TypeError: can only concatenate str (not "Style") to str

    # [ins] In [16]: edit 33_bottom_toolbar.py
    # Editing... done. Executing edited code...
    # ---------------------------------------------------------------------------
    # TypeError                                 Traceback (most recent call last)
    # ~/projects/dynamic_ipython/default_profile/startup/33_bottom_toolbar.py in <module>
    #     244     bottom_toolbar = FormattedTextToolbar(PygmentsTokens(bottom_text), style=style)
    #     245     add_toolbar(bottom_text)
    # --> 246     print_container(show_header())
    #         global print_container = <function print_container at 0x73eefc0670>
    #         global show_header = <function show_header at 0x73ebb4c040>

    # ~/projects/dynamic_ipython/default_profile/startup/33_bottom_toolbar.py in show_header(header_text='Press Control-Y to paste from the system clipboa...ction mode.\nPress Control-W to cut to clipboard.\n')
    #      79         )
    #      80     # TODO: Should replace that text with somethin else
    # ---> 81     text_area = TextArea(header_text, style=style_from_pygments_cls(InkPotStyle()))
    #         text_area = undefined
    #         global TextArea = <class 'prompt_toolkit.widgets.base.TextArea'>
    #         header_text = 'Press Control-Y to paste from the system clipboard.\nPress Control-Space or Control-@ to enter selection mode.\nPress Control-W to cut to clipboard.\n'
    #         global style = <prompt_toolkit.styles.style.Style object at 0x73eb378d30>
    #         global style_from_pygments_cls = <function style_from_pygments_cls at 0x73ef4dbee0>
    #         global InkPotStyle = <class 'pygments.styles.inkpot.InkPotStyle'>
    #      82     # its legitimately insane to me that this raises.
    #      83     # TODO: Changes what a style is

    # ~/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/prompt_toolkit/styles/pygments.py in style_from_pygments_cls(pygments_style_cls=<pygments.styles.inkpot.InkPotStyle object>)
    #      39     from pygments.style import Style as PygmentsStyle
    #      40
    # ---> 41     assert issubclass(pygments_style_cls, PygmentsStyle)
    #         global issubclass = undefined
    #         pygments_style_cls = <pygments.styles.inkpot.InkPotStyle object at 0x73eb1e0e20>
    #         PygmentsStyle = <class 'pygments.style.Style'>
    #      42
    #      43     return style_from_pygments_dict(pygments_style_cls.styles)

    # TypeError: issubclass() arg 1 must be a class

    text_area = TextArea(header_text, style="#ebdbb2")
    # its legitimately insane to me that all 3 raises.
            # style=style_from_pygments_cls(InkPotStyle()))
            # style=style_from_pygments_cls(InkPotStyle))
    # TODO: Changes what a style is
    # style=[("toolbar", "#ebdbb2")])
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

    As the bottom_toolbar property exists in both a prompt_toolkit
    PromptSession and Application, both are accessible from the `session`
    and `pt_app` attributes.

    Defines a method :meth:`rerender` and calls it whenever the instance
    is called via ``__call__``.

    Examples
    --------
    >>> bt = BottomToolbar(get_app())
    >>> print(bt)
        <BottomToolbar:>
    >>> bt()
        f" [F4] Vi: {current_vi_mode!r} \n  cwd: {Path.cwd().stem!r}\n Clock: {time.ctime()!r}"

    """
    # are you allowed to doctest fstrings

    def __init__(self, app, *args, **kwargs):
        """Require an 'app' for initialization.

        This will eliminate all IPython code out of this class and make things
        a little more modular for the tests.
        """
        self.shell = get_ipython()
        self.app = app
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
        return f"<{self.__class__.__name__!r}:>"

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
        toolbar = f" [F4] Vi: {current_vi_mode!r} \n  cwd: {Path.cwd().stem!r}\n Clock: {time.ctime()!r}"
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
            if _ip.pt_app.bottom_toolbar is None:
                _ip.pt_app.bottom_toolbar = toolbar


if __name__ == "__main__":
    # bottom_formatted_text = FormattedText(
    #     BottomToolbar(get_app()), style=("class:toolbar", "underline #80a0ff")
    # )
    bottom_text = BottomToolbar(get_app())
    partial_window = Window(
        FormattedTextControl(bottom_text), width=60, height=3, style=pygments_style
    )

    style = Style.from_dict(
        {
            "dialog": "bg:#cdbbb3",
            "button": "bg:#bf99a4",
            "checkbox": "#e8612c",
            "dialog.body": "bg:#a9cfd0",
            "dialog shadow": "bg:#c98982",
            "frame.label": "#fcaca3",
            "dialog.body label": "#fd8bb6",
        }
    )

    example_style = Style.from_dict(
        {
            "dialog": "bg:#88ff88",
            "dialog frame.label": "bg:#ffffff #000000",
            "dialog.body": "bg:#000000 #00ff00",
            "dialog shadow": "bg:#00aa00",
        }
    )
    # Do frames not return container objects? Because this line is raisin an error?
    # bottom_float = Float(Frame(partial_window, style="bg:#282828 #ffffff"), bottom=0)
    # print_container(bottom_float)
    bottom_toolbar = FormattedTextToolbar(PygmentsTokens(bottom_text), style=style)
    add_toolbar(bottom_text)
    print_container(show_header())
