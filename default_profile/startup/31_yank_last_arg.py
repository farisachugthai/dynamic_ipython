"""
Started with:

https://gist.githubusercontent.com/konradkonrad/7143fa8407804e37132e4ea90175f2d8/raw/ef2f570fc67fd5d9d227f9ae0363e10907831c97/01-esc-dot.py

Has since grown to ~200 key bindings.
"""
from IPython.core.getipython import get_ipython
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import (EmacsInsertMode, HasFocus, HasSelection,
                                    ViInsertMode)
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.bindings.auto_suggest import \
    load_auto_suggest_bindings
from prompt_toolkit.key_binding.bindings.basic import load_basic_bindings
from prompt_toolkit.key_binding.bindings.completion import \
    display_completions_like_readline
from prompt_toolkit.key_binding.bindings.cpr import load_cpr_bindings
from prompt_toolkit.key_binding.bindings.emacs import (
    load_emacs_bindings, load_emacs_search_bindings)
from prompt_toolkit.key_binding.bindings.mouse import load_mouse_bindings
from prompt_toolkit.key_binding.bindings.open_in_editor import \
    load_open_in_editor_bindings
from prompt_toolkit.key_binding.bindings.page_navigation import \
    load_page_navigation_bindings
from prompt_toolkit.keys import Keys

insert_mode = ViInsertMode() | EmacsInsertMode()


def get_key_bindings(custom_key_bindings=None):
    """
    The ``__init__`` for `_MergedKeyBindings` features this.:

        def __init__(self, registries):
            assert all(isinstance(r, KeyBindingsBase) for r in registries)
            _Proxy.__init__(self)
            self.registries = registries

    As a result `None` can't be passed to merge_key_bindings.

    Based on prompt_toolkit.key_binding.defaults.load_key_bindings()
    """
    if custom_key_bindings is None:
        custom_key_bindings = KeyBindings()
    return [
        load_auto_suggest_bindings(),
        load_basic_bindings(),
        load_cpr_bindings(),
        load_emacs_bindings(),
        load_emacs_search_bindings(),
        load_mouse_bindings(),
        load_open_in_editor_bindings(),
        load_page_navigation_bindings(),
        custom_key_bindings,
    ]


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

    .. see: https://www.gnu.org/software/bash/manual/bashref.html#Commands-For-History

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


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    # logger.debug('%s', dir(event))
    vi_state.input_mode = InputMode.NAVIGATION


if __name__ == "__main__":
    registry = KeyBindings()

    ip = get_ipython()

    if getattr(ip, "pt_app", None):
        orig_kb = ip.pt_app.app.key_bindings

    elif getattr(ip, "pt_cli", None):
        orig_kb = ip.pt_cli.application.key_bindings_registry
    else:
        raise NotImplementedError(
            "IPython doesn't have prompt toolkit bindings. Exiting.")

    registry.add_binding(
        Keys.Escape,
        u".",
        filter=(HasFocus(DEFAULT_BUFFER) & ~HasSelection() & insert_mode),
    )(yank_last_arg)
    registry.add_binding(
        Keys.Escape,
        u"_",
        filter=(HasFocus(DEFAULT_BUFFER) & ~HasSelection() & insert_mode),
    )(yank_last_arg)

    ip.events.register("post_execute", reset_last_arg_depth)

    registry.add(Keys.ControlI, filter=(HasFocus(DEFAULT_BUFFER) & insert_mode))(display_completions_like_readline)

    registry.add("j", "k", filter=(HasFocus(DEFAULT_BUFFER) & insert_mode))(switch_to_navigation_mode)
    # Keys.j and Keys.k don't exists
    # registry.add(Keys.j, Keys.k)(switch_to_navigation_mode)
    # add allll the defaults in and bind it back to the shell.
    # If we did this correctly, running _ip.pt_app.app.key_bindings.bindings
    # should display something like +100 bindings
    # since we linked it to the correct attribute of pt_app this should work

    # all_kb = get_key_bindings(registry)
    # Overwrite our original keybindings
    # orig_kb = all_kb
    # _ip.pt_app.app.key_bindings = load_key_bindings()
