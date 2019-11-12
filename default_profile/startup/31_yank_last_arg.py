"""
https://gist.githubusercontent.com/konradkonrad/7143fa8407804e37132e4ea90175f2d8/raw/ef2f570fc67fd5d9d227f9ae0363e10907831c97/01-esc-dot.py
"""
# ~/.ipython/profile_default/startup/01-esc-dot.py
from IPython import get_ipython
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import HasFocus, HasSelection, ViInsertMode, EmacsInsertMode

ip = get_ipython()
insert_mode = ViInsertMode() | EmacsInsertMode()


class State:
    def __init__(self):
        self.depth = 0


state = State()


def reset_last_arg_depth():
    state.depth = 0


def yank_last_arg(event):
    """:program:`readline` style 'yank-last-arg'

    Insert last argument to the previous command (the last word of the
    previous history entry).

    Successive calls to yank-last-arg move back through the history list,
    inserting the last word of each line in turn.

    .. see:: https://www.gnu.org/software/bash/manual/bashref.html#Commands-For-History

    .. note: This doesn't support the numeric argument option of readline's
             yank-last-arg

    """
    b = event.current_buffer
    hist = ip.history_manager.input_hist_raw
    if state.depth == 0:
        state.depth = 1
    else:
        state.depth += 1

    if len(hist) and len(hist) >= state.depth:
        lastline = hist[-state.depth]

        if state.depth > 1:
            b.undo()

        b.save_to_undo_stack()
        if len(lastline.split()):
            b.insert_text(lastline.split()[-1])


if __name__ == "__main__":
    # TODO: Come up with an else because prompt_toolkit might not bind through
    # the pt_cli attr anymore
    if getattr(ip, "pt_app"):
        registry = ip.pt_app.key_bindings
    elif getattr(ip, "pt_cli"):
        registry = ip.pt_cli.application.key_bindings_registry

    registry.add_binding(
        Keys.Escape,
        ".",
        filter=(HasFocus(DEFAULT_BUFFER) & ~HasSelection() & insert_mode),
    )(yank_last_arg)
    registry.add_binding(
        Keys.Escape,
        "_",
        filter=(HasFocus(DEFAULT_BUFFER) & ~HasSelection() & insert_mode),
    )(yank_last_arg)
    ip.events.register("post_execute", reset_last_arg_depth)
