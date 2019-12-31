"""Holy fuck this works."""
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

from IPython.core.getipython import get_ipython

# Add an additional key binding for toggling this flag.
# don't really get the point of making a new container for t though
toggle_vi = KeyBindings()


def bottom_toolbar():
    """Display the current input mode.

    Got a TypeError because function doesn't have len?
    Wtf dude.
    """
    if get_ipython().pt_app.app.editing_mode == EditingMode.VI:
        current_vi_mode = get_ipython().pt_app.app.vi_state.input_mode
        return " [F4] Vi: {}".format(current_vi_mode)
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
