"""Holy fuck this works."""
from datetime import date
from pathlib import Path
import functools
from traceback import print_exception

from prompt_toolkit import ANSI, HTML
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.shortcuts import print_formatted_text, CompleteStyle
from prompt_toolkit.styles import default_pygments_style

from prompt_toolkit.styles import merge_styles, Style
from prompt_toolkit.styles.pygments import (
    style_from_pygments_cls,
    style_from_pygments_dict,
)

from IPython.core.getipython import get_ipython

try:
    from gruvbox.style import GruvboxDarkHard
except:
    GruvboxDarkHard = None

# Add an additional key binding for toggling this flag.
# don't really get the point of making a new container for t though
toggle_vi = KeyBindings()


class BottomToolbar:
    """Display the current input mode.

    Ooo this might be a fun time to really see how far I can stretch
    pythons new string formatting.
    """

    completion_displays_to_styles = {
        "multi": CompleteStyle.MULTI_COLUMN,
        "single": CompleteStyle.COLUMN,
        "readline": CompleteStyle.READLINE_LIKE,
        "none": None,
    }

    def __init__(self):
        self.shell = get_ipython()
        self.unfinished_toolbar = ""
        self.rerender()

    @property
    def session(self):
        return self.shell.pt_app

    @property
    def pt_app(self):
        # TODO: Be more consistent and check multiple versions of pt as done in other files
        return self.shell.pt_app.app

    @property
    def is_vi_mode(self):
        if self.pt_app.editing_mode == EditingMode.VI:
            return True
        else:
            return False

    def __call__(self):
        self.rerender()

    def rerender(self):
        if self.is_vi_mode:
            return self._render_vi()
        else:
            return self._render_emacs()

    def _render_vi(self):
        # TODO:
        # add more styling:
        # [('class:toolbar', ' [F4] %s ' % text)]
        current_vi_mode = self.pt_app().vi_state.input_mode
        toolbar = f" [F4] Vi: {current_vi_mode}  {date.today()}"
        return toolbar

    def _render_emacs(self):
        return f" [F4] Emacs: {Path.cwd()} {date.today()}"

    def override_style(self):
        """Could be easily modified to utilize traitlets."""
        style_overrides_env = env.get("PTK_STYLE_OVERRIDES")
        if style_overrides_env:
            try:
                style_overrides = Style.from_dict(style_overrides_env)
                prompt_args["style"] = merge_styles([style, style_overrides])
            except (AttributeError, TypeError, ValueError):
                print_exception()


@toggle_vi.add(Keys.F4)
def _(event):
    # The syntax of this function alone is the argument for more dunders.
    if event.app.editing_mode == "VI":
        return "EMACS"
    if event.app.editing_mode == "EMACS":
        return "VI"


def add_toolbar(toolbar=None):
    """Get the running IPython instance and add 'bottom_toolbar'."""
    _ip = get_ipython()

    @toggle_vi.add(Keys.F4)
    def _(event):
        """Toggle between Emacs and Vi mode."""
        if event.app.editing_mode == EditingMode.VI:
            event.app.editing_mode = EditingMode.EMACS
        else:
            event.app.editing_mode = EditingMode.VI

    _ip.pt_app.bottom_toolbar = toolbar.rerender()


# Don't uncomment! This fucks up the keybindings so that the only way a line
# executes is if you use C-r to get into a search then hit something to regain
# focus and then hit enter.
# Unbelievable. It wasn't this block. it was load_key_bindings()?????
if __name__ == "__main__":
    if get_ipython() is not None:
        bottom_toolbar = BottomToolbar()
        add_toolbar(bottom_toolbar)
