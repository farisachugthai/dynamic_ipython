"""Holy fuck this works."""
from datetime import date
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

# from prompt_toolkit.shortcuts import HTML
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.styles import default_pygments_style

from IPython.core.getipython import get_ipython

# Add an additional key binding for toggling this flag.
# don't really get the point of making a new container for t though
toggle_vi = KeyBindings()


def bottom_toolbar():
    """Display the current input mode.

    Got a TypeError because function doesn't have len?
    Wtf dude.

    Ooo this might be a fun time to really see how far I can stretch
    pythons new string formatting.
    """
    if get_ipython().pt_app.app.editing_mode == EditingMode.VI:
        current_vi_mode = get_ipython().pt_app.app.vi_state.input_mode
        return print_formatted_text(
            " [F4] Vi: {}  {:>30}".format(current_vi_mode, date.today()),
            style=default_pygments_style(),
        )
    else:
        return " [F4] Emacs "


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

    _ip.pt_app.bottom_toolbar = bottom_toolbar

    _ip.pt_app.app.key_bindings.registries.append(toggle_vi)


# Don't uncomment! This fucks up the keybindings so that the only way a line
# executes is if you use C-r to get into a search then hit something to regain
# focus and then hit enter.
# Unbelievable. It wasn't this block. it was load_key_bindings()?????
if __name__ == "__main__":
    if get_ipython() is not None:
        add_toolbar()
