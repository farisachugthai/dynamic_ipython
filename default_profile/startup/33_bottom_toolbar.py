"""Holy fuck this works."""
from datetime import date

from prompt_toolkit import ANSI, HTML
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

# from prompt_toolkit.shortcuts import HTML
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.styles import default_pygments_style

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

    def __init__(self):
        self.shell = get_ipython()
        self.unfinished_toolbar = ''

    def get_ipython_promptsession(self):
        return shell.pt_app

    def get_ipython_app(self):
        # TODO: Be more consistent and check multiple versions of pt as done in other files
        return shell.pt_app.app

    @property
    def is_vi_mode(self):
        if get_ipython().pt_app.app.editing_mode == EditingMode.VI:
            return True

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
        current_vi_mode = self.get_ipython_app().vi_state.input_mode
        toolbar = [
                format(" [F4] Vi: {}  {:>30}", current_vi_mode, date.today()),
            ]
        toolbar.append(style=default_pygments_style())
        return toolbar

    def _render_emacs(self):
        return " Emacs "


@toggle_vi.add(Keys.F4)
def _(event):
    # The syntax of this function alone is the argument for more dunders.
    if event.app.editing_mode == 'VI':
        return 'EMACS'
    if event.app.editing_mode == 'EMACS':
        return 'VI'


def toggle_editing_mode(_ip):
    _ip.pt_app.app.key_bindings.registries.append(toggle_vi)


def add_toolbar():
    """Get the running IPython instance and add 'bottom_toolbar'."""
    _ip = get_ipython()

    @toggle_vi.add(Keys.F4)
    def toggled(event):
        """Toggle between Emacs and Vi mode."""
        if event.app.editing_mode == EditingMode.VI:
            event.app.editing_mode = EditingMode.EMACS
        else:
            event.app.editing_mode = EditingMode.VI

    bottom_toolbar = BottomToolbar()
    bottom_toolbar.rerender()
    _ip.pt_app.bottom_toolbar = bottom_toolbar.rerender()



# Don't uncomment! This fucks up the keybindings so that the only way a line
# executes is if you use C-r to get into a search then hit something to regain
# focus and then hit enter.
# Unbelievable. It wasn't this block. it was load_key_bindings()?????
if __name__ == "__main__":
    if get_ipython() is not None:
        add_toolbar()
