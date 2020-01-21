"""
Started with:

https://gist.githubusercontent.com/konradkonrad/7143fa8407804e37132e4ea90175f2d8/raw/ef2f570fc67fd5d9d227f9ae0363e10907831c97/01-esc-dot.py

Has since grown to ~200 key bindings.
"""
from IPython.core.getipython import get_ipython
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import (
    Condition,
    has_selection,
    in_paste_mode,
    is_multiline,
)
from prompt_toolkit.filters.app import emacs_insert_mode, vi_insert_mode, has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.auto_suggest import load_auto_suggest_bindings
from prompt_toolkit.key_binding.bindings.basic import load_basic_bindings
from prompt_toolkit.key_binding.bindings.completion import (
    display_completions_like_readline,
)
from prompt_toolkit.key_binding.bindings.cpr import load_cpr_bindings
from prompt_toolkit.key_binding.bindings.emacs import (
    load_emacs_bindings,
    load_emacs_search_bindings,
)
from prompt_toolkit.key_binding.bindings.mouse import load_mouse_bindings
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
from prompt_toolkit.key_binding.bindings.open_in_editor import (
    load_open_in_editor_bindings,
)
from prompt_toolkit.key_binding.bindings.page_navigation import (
    load_page_navigation_bindings,
)
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyPressEvent
from prompt_toolkit.keys import Keys

# fun fact. ViInsertMode is deprecated
insert_mode = vi_insert_mode() | emacs_insert_mode()


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


E = KeyPressEvent


def if_no_repeat(event: E) -> bool:
    """ Callable that returns True when the previous event was delivered to
    another handler. """
    return not event.is_repeat


def additional_bindings():
    registry = KeyBindings()

    ip = get_ipython()

    if getattr(ip, "pt_app", None):
        orig_kb = ip.pt_app.app.key_bindings

    elif getattr(ip, "pt_cli", None):
        orig_kb = ip.pt_cli.application.key_bindings_registry
    else:
        raise NotImplementedError(
            "IPython doesn't have prompt toolkit bindings. Exiting."
        )

    registry.add_binding(Keys.Escape, u".")(yank_last_arg)
    registry.add_binding(Keys.Escape, u"_")(yank_last_arg)
    ip.events.register("post_execute", reset_last_arg_depth)
    registry.add(Keys.ControlI)(display_completions_like_readline)

    registry.add("j", "k")(switch_to_navigation_mode)
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

    # From prompt_toolkit.key_binding.key_bindings.basic
    handle = registry.add

    handle("home")(get_by_name("beginning-of-line"))
    handle("end")(get_by_name("end-of-line"))
    handle("left")(get_by_name("backward-char"))
    handle("right")(get_by_name("forward-char"))
    handle("c-up")(get_by_name("previous-history"))
    handle("c-down")(get_by_name("next-history"))
    handle("c-l")(get_by_name("clear-screen"))

    handle("c-k", filter=insert_mode)(get_by_name("kill-line"))
    handle("c-u", filter=insert_mode)(get_by_name("unix-line-discard"))
    handle("backspace", filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("backward-delete-char")
    )
    handle("delete", filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("delete-char")
    )
    handle("c-delete", filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("delete-char")
    )
    handle(Keys.Any, filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("self-insert")
    )
    handle("c-t", filter=insert_mode)(get_by_name("transpose-chars"))
    handle("c-i", filter=insert_mode)(get_by_name("menu-complete"))
    handle("s-tab", filter=insert_mode)(get_by_name("menu-complete-backward"))

    # Control-W should delete, using whitespace as separator, while M-Del
    # should delete using [^a-zA-Z0-9] as a boundary.
    handle("c-w", filter=insert_mode)(get_by_name("unix-word-rubout"))

    handle("pageup", filter=~has_selection)(get_by_name("previous-history"))
    handle("pagedown", filter=~has_selection)(get_by_name("next-history"))

    # CTRL keys.

    @Condition
    def has_text_before_cursor() -> bool:
        return bool(get_app().current_buffer.text)

    handle("c-d")(get_by_name("delete-char"))

    @handle("enter")
    def _(event: E) -> None:
        """
        Newline (in case of multiline input.
        """
        event.current_buffer.newline(copy_margin=not in_paste_mode())

    @handle("c-j")
    def _(event: E) -> None:
        r"""
        By default, handle \n as if it were a \r (enter).
        (It appears that some terminals send \n instead of \r when pressing
        enter. - at least the Linux subsystem for Windows.)
        """
        event.key_processor.feed(KeyPress(Keys.ControlM, "\r"), first=True)

    # Delete the word before the cursor.

    @handle("up")
    def _(event: E) -> None:
        event.current_buffer.auto_up(count=event.arg)

    @handle("down")
    def _(event: E) -> None:
        event.current_buffer.auto_down(count=event.arg)

    @handle("delete", filter=has_selection)
    def _(event: E) -> None:
        data = event.current_buffer.cut_selection()
        event.app.clipboard.set_data(data)

    # Global bindings.

    @handle("c-z")
    def _(event: E) -> None:
        """
        By default, control-Z should literally insert Ctrl-Z.
        (Ansi Ctrl-Z, code 26 in MSDOS means End-Of-File.
        In a Python REPL for instance, it's possible to type
        Control-Z followed by enter to quit.)
        When the system bindings are loaded and suspend-to-background is
        supported, that will override this binding.
        """
        event.current_buffer.insert_text(event.data)

    @handle(Keys.BracketedPaste)
    def _(event: E) -> None:
        """
        Pasting from clipboard.
        """
        data = event.data

        # Be sure to use \n as line ending.
        # Some terminals (Like iTerm2) seem to paste \r\n line endings in a
        # bracketed paste. See: https://github.com/ipython/ipython/issues/9737
        data = data.replace("\r\n", "\n")
        data = data.replace("\r", "\n")

        event.current_buffer.insert_text(data)

    @Condition
    def in_quoted_insert() -> bool:
        return get_app().quoted_insert

    @handle(Keys.Any, filter=in_quoted_insert, eager=True)
    def _(event: E) -> None:
        """
        Handle quoted insert.
        """
        event.current_buffer.insert_text(event.data, overwrite=False)
        event.app.quoted_insert = False

    return registry


if __name__ == "__main__":
    additional_bindings()
