"""Add keybindings.

Slowly becoming where all my consolidated scripts for making prompt_toolkit's
handling of keypresses cohesive.

TODO: still need C-d, C-c.

However <CR> and <C-m> work as expected. haven't even tried navigation mode;
however, there's supposed to be ~500 key bindings so I'm excited.

"""
from collections import namedtuple

from prompt_toolkit.application.current import get_app

# from prompt_toolkit.buffer import YankNthArgState
from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import (
    Condition,
    IsMultiline,
    IsSearching,
    in_paste_mode,
)

from prompt_toolkit.filters.app import emacs_insert_mode, vi_insert_mode, has_focus

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.completion import (
    display_completions_like_readline,
)
from prompt_toolkit.key_binding.bindings.named_commands import (
    accept_line,
    self_insert,
    backward_delete_char,
    get_by_name,
)
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyPressEvent
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.keys import Keys

from prompt_toolkit.input.vt100_parser import ANSI_SEQUENCES

from prompt_toolkit.selection import SelectionState

from IPython.core.getipython import get_ipython
from IPython.terminal.shortcuts import create_ipython_shortcuts

E = KeyPressEvent

DEDENT_TOKENS = frozenset(["raise", "return", "pass", "break", "continue"])


# Conditions:

# fun fact. ViInsertMode is deprecated
insert_mode = vi_insert_mode() | emacs_insert_mode()


@Condition
def should_confirm_completion():
    """Check if completion needs confirmation"""
    return get_app().current_buffer.complete_state


@Condition
def has_text_before_cursor() -> bool:
    return bool(get_app().current_buffer.text)


@Condition
def ctrl_d_condition():
    """Ctrl-D binding is only active when the default buffer is selected and
    empty.
    """
    app = get_app()
    buffer_name = app.current_buffer.name

    return buffer_name == DEFAULT_BUFFER and not app.current_buffer.text


# This is erroring...is it because its the only condition that requires an argument?
# @Condition
# def _is_blank(l):
#     return len(l.strip()) == 0


@Condition
def tab_insert_indent():
    """Check if <Tab> should insert indent instead of starting autocompletion.
    Checks if there are only whitespaces before the cursor - if so indent
    should be inserted, otherwise autocompletion.

    """
    before_cursor = get_app().current_buffer.document.current_line_before_cursor

    return bool(before_cursor.isspace())


@Condition
def beginning_of_line():
    """Check if cursor is at beginning of a line other than the first line in a
    multiline document
    """
    app = get_app()
    before_cursor = app.current_buffer.document.current_line_before_cursor

    return bool(
        len(before_cursor) == 0 and not app.current_buffer.document.on_first_line
    )


@Condition
def end_of_line():
    """Check if cursor is at the end of a line other than the last line in a
    multiline document
    """
    d = get_app().current_buffer.document
    at_end = d.is_cursor_at_the_end_of_line
    last_line = d.is_cursor_at_the_end

    return bool(at_end and not last_line)


@Condition
def whitespace_or_bracket_before():
    """Check if there is whitespace or an opening
       bracket to the left of the cursor"""
    d = get_app().current_buffer.document
    return bool(
        d.cursor_position == 0
        or d.char_before_cursor.isspace()
        or d.char_before_cursor in "([{"
    )


@Condition
def whitespace_or_bracket_after():
    """Check if there is whitespace or a closing
       bracket to the right of the cursor"""
    d = get_app().current_buffer.document
    return bool(
        d.is_cursor_at_the_end_of_line
        or d.current_char.isspace()
        or d.current_char in ")]}"
    )


@Condition
def in_quoted_insert() -> bool:
    return get_app().quoted_insert


@Condition
def is_multiline():
    return document_is_multiline_python(python_input.default_buffer.document)


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    # logger.debug('%s', dir(event))
    vi_state.input_mode = InputMode.NAVIGATION


def if_no_repeat(event: E) -> bool:
    """ Callable that returns True when the previous event was delivered to
    another handler. """
    return not event.is_repeat


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
    from prompt_toolkit.key_binding.bindings.auto_suggest import (
        load_auto_suggest_bindings,
    )
    from prompt_toolkit.key_binding.bindings.basic import load_basic_bindings
    from prompt_toolkit.key_binding.bindings.cpr import load_cpr_bindings
    from prompt_toolkit.key_binding.bindings.vi import (
        load_vi_bindings,
        load_vi_search_bindings,
    )
    from prompt_toolkit.key_binding.bindings.mouse import load_mouse_bindings
    from prompt_toolkit.key_binding.bindings.open_in_editor import (
        load_open_in_editor_bindings,
    )
    from prompt_toolkit.key_binding.bindings.page_navigation import (
        load_page_navigation_bindings,
    )

    if custom_key_bindings is None:
        custom_key_bindings = KeyBindings()
    return [
        load_auto_suggest_bindings(),
        load_basic_bindings(),
        load_cpr_bindings(),
        load_vi_bindings(),
        load_vi_search_bindings(),
        load_mouse_bindings(),
        load_open_in_editor_bindings(),
        load_page_navigation_bindings(),
        create_ipython_shortcuts(get_ipython()),
        custom_key_bindings,
    ]


def add_bindings():
    registry = KeyBindings()

    handle = registry.add
    # So I think we can get away without using these because Buffer.yank_last_arg and others exist
    # handle(Keys.Escape, u".")(yank_last_arg)
    # handle(Keys.Escape, u"_")(yank_last_arg)
    # ip = get_ipython()
    # ip.events.register("post_execute", reset_last_arg_depth)
    registry.add(Keys.ControlI)(display_completions_like_readline)

    registry.add("j", "k")(switch_to_navigation_mode)
    # From prompt_toolkit.key_binding.key_bindings.basic

    handle("home")(get_by_name("beginning-of-line"))
    handle(Keys.ControlA)(get_by_name("beginning-of-line"))

    handle("end")(get_by_name("end-of-line"))
    handle(Keys.ControlE)(get_by_name("end-of-line"))

    # alternatively:

    @handle(Keys.Escape, "<")
    def beginning(event):
        """Move to the beginning of our recorded history."""
        event.current_buffer.cursor_position = 0

    @handle(Keys.Escape, ">")
    def end(event):
        """Move to the end."""
        event.current_buffer.cursor_position = len(event.current_buffer.text)

    # handle("left")(get_by_name("backward-char"))
    # handle("right")(get_by_name("forward-char"))


    is_returnable = Condition(
        lambda: get_app().current_buffer.is_returnable)

    @handle(Keys.Left)
    def left_multiline(event):
        """
        Left that wraps around in multiline.
        """
        if event.current_buffer.cursor_position - event.arg >= 0:
            event.current_buffer.cursor_position -= event.arg

        if getattr(event.current_buffer.selection_state, "shift_arrow", False):
            event.current_buffer.selection_state = None

    @handle(Keys.Right)
    def right_multiline(event):
        """
        Right that wraps around in multiline.
        """
        if event.current_buffer.cursor_position + event.arg <= len(
            event.current_buffer.text
        ):
            event.current_buffer.cursor_position += event.arg

        if getattr(event.current_buffer.selection_state, "shift_arrow", False):
            event.current_buffer.selection_state = None

    # Speaking of multiline
    @handle(Keys.Enter, filter=is_returnable)
    def multiline_enter(event):
        """
        When not in multiline, execute. When in multiline, try to
        intelligently add a newline or execute.
        """
        buffer = event.current_buffer
        document = buffer.document
        # multiline = document_is_multiline_python(document)

        text_after_cursor = document.text_after_cursor
        text_before_cursor = document.text_before_cursor
        text = buffer.text
        # isspace doesn't respect vacuous truth
        if (
            not text_after_cursor or text_after_cursor.isspace()
        ) and text_before_cursor.replace(" ", "").endswith("\n"):
            # If we are at the end of the buffer, accept unless we are in a
            # docstring
            row, col = document.translate_index_to_position(buffer.cursor_position)
            row += 1
            accept_line(event)
        else:
            accept_line(event)
        # elif not multiline:
        # Always accept a single valid line. Also occurs for unclosed single
        # quoted strings (which will give a syntax error)
        # accept_line(event)
        # else:
        #     auto_newline(event.current_buffer)

    # Always accept the line if the previous key was Up
    # Requires https://github.com/jonathanslenders/python-prompt-toolkit/pull/492.
    # We don't need a parallel for down because down is already at the end of the
    # prompt.

    @handle(Keys.Enter, filter=is_returnable)
    def accept_after_history_backward(event):
        pks = event.previous_key_sequence
        if (
            pks
            and getattr(pks[-1], "accept_next", False)
            and (
                (len(pks) == 1 and pks[0].key == "up")
                or (
                    len(pks) == 2
                    and pks[0].key == "escape"
                    and isinstance(pks[1].key, str)
                    and pks[1].key in "pP"
                )
            )
        ):
            accept_line(event)
        else:
            multiline_enter(event)


    @handle(Keys.ControlX, Keys.ControlE)
    def open_in_editor(event):
        event.current_buffer.open_in_editor(event.app)


    handle("c-up")(get_by_name("previous-history"))
    handle(Keys.ControlP)(get_by_name("previous-history"))
    handle("c-down")(get_by_name("next-history"))
    handle(Keys.ControlN)(get_by_name("next-history"))
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

    # TODO: FZF
    handle("c-t", filter=insert_mode)(get_by_name("transpose-chars"))
    handle("c-i", filter=insert_mode)(get_by_name("menu-complete"))
    handle("s-tab", filter=insert_mode)(get_by_name("menu-complete-backward"))

    # Control-W should delete, using whitespace as separator, while M-Del
    # should delete using [^a-zA-Z0-9] as a boundary.
    handle("c-w", filter=insert_mode)(get_by_name("unix-word-rubout"))

    handle("pageup")(get_by_name("previous-history"))
    handle("pagedown")(get_by_name("next-history"))

    handle("c-d")(get_by_name("delete-char"))

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

    @handle("delete")
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
        if event.app.enable_system_bindings:
            event.app.suspend_to_background()
        else:
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

    @handle(Keys.Any, filter=in_quoted_insert, eager=True)
    def _(event: E) -> None:
        """
        Handle quoted insert.
        """
        event.current_buffer.insert_text(event.data, overwrite=False)
        event.app.quoted_insert = False

    @handle("f4")
    def _(event):
        """Toggle between Vi and Emacs mode.

        See Also
        --------
        `34_bottom_toolbar`
            Utilized for this purpose.
        """
        event.app.editing_mode = not event.app.editing_mode == "vi"

    @handle("f6")
    def _(event):
        """
        Enable/Disable paste mode.
        """
        event.app.paste_mode = not event.app.paste_mode



    @handle(Keys.ControlC)
    def _(event):
        """
        Pressing Ctrl-C will exit the user interface.
        Setting a return value means: quit the event loop that drives the user
        interface and return this value from the `Application.run()` call.
        """
        event.app.exit()

    @handle(Keys.ControlD)
    def _(event):
        raise EOFError

    @handle(Keys.ControlX, Keys.ControlE, filter=~has_selection)
    def open_editor(event):
        """ Open current buffer in editor """
        event.current_buffer.open_in_editor(event.cli)

    @handle(Keys.Tab, filter=tab_insert_indent)
    def insert_indent(event):
        """
        If there are only whitespaces before current cursor position insert
        indent instead of autocompleting.
        """
        event.cli.current_buffer.insert_text()

    @handle(Keys.BackTab, filter=insert_mode)
    def insert_literal_tab(event):
        """ Insert literal tab on Shift+Tab instead of autocompleting """
        b = event.current_buffer
        if b.complete_state:
            b.complete_previous()
        else:
            event.cli.current_buffer.insert_text("    "))

    @handle("(", filter=autopair_condition & whitespace_or_bracket_after)
    def insert_right_parens(event):
        event.cli.current_buffer.insert_text("(")
        event.cli.current_buffer.insert_text(")", move_cursor=False)

    @handle(")", filter=autopair_condition)
    def overwrite_right_parens(event):
        buffer = event.cli.current_buffer
        if buffer.document.current_char == ")":
            buffer.cursor_position += 1
        else:
            buffer.insert_text(")")

    @handle("[", filter=autopair_condition & whitespace_or_bracket_after)
    def insert_right_bracket(event):
        event.cli.current_buffer.insert_text("[")
        event.cli.current_buffer.insert_text("]", move_cursor=False)

    @handle("]", filter=autopair_condition)
    def overwrite_right_bracket(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "]":
            buffer.cursor_position += 1
        else:
            buffer.insert_text("]")

    @handle("{", filter=autopair_condition & whitespace_or_bracket_after)
    def insert_right_brace(event):
        event.cli.current_buffer.insert_text("{")
        event.cli.current_buffer.insert_text("}", move_cursor=False)

    @handle("}", filter=autopair_condition)
    def overwrite_right_brace(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "}":
            buffer.cursor_position += 1
        else:
            buffer.insert_text("}")

    @handle("'", filter=autopair_condition)
    def insert_right_quote(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "'":
            buffer.cursor_position += 1
        elif whitespace_or_bracket_before() and whitespace_or_bracket_after():
            buffer.insert_text("'")
            buffer.insert_text("'", move_cursor=False)
        else:
            buffer.insert_text("'")

    @handle('"', filter=autopair_condition)
    def insert_right_double_quote(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == '"':
            buffer.cursor_position += 1
        elif whitespace_or_bracket_before() and whitespace_or_bracket_after():
            buffer.insert_text('"')
            buffer.insert_text('"', move_cursor=False)
        else:
            buffer.insert_text('"')

    @handle(Keys.Backspace, filter=autopair_condition)
    def delete_brackets_or_quotes(event):
        """Delete empty pair of brackets or quotes"""
        buffer = event.cli.current_buffer
        before = buffer.document.char_before_cursor
        after = buffer.document.current_char

        if any(
            [before == b and after == a for (b, a) in ["()", "[]", "{}", "''", '""']]
        ):
            buffer.delete(1)

        buffer.delete_before_cursor(1)


    return registry


if __name__ == "__main__":

    _ip = get_ipython()
    if _ip is not None:
        _ip.pt_app.app.output.enable_bracketed_paste()
        bindings = add_bindings()
        extra_bindings = merge_key_bindings(get_key_bindings(bindings))
        _ip.pt_app.app.key_bindings = extra_bindings
        # _ip.pt_app.app.key_bindings._update_cache()
    else:
        sys.exit()
