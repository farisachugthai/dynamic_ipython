"""Add keybindings.

Slowly becoming where all my consolidated scripts for making prompt_toolkit's
handling of keypresses cohesive.

TODO: still need C-z
Tab doesn't start autocompletion when no letters have been typed in.
Damnit I lost C-d again.

However <CR> and <C-m> work as expected. haven't even tried navigation mode;
however, there's supposed to be ~500 key bindings so I'm excited.

"""
from collections import namedtuple
import ctypes
import functools
from traceback import print_exception

# from prompt_toolkit.application.current import get_app
from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import (
    Condition,
    is_searching,
    in_paste_mode,
    buffer_has_focus,
)
from prompt_toolkit.filters.app import (
    vi_navigation_mode,
    is_multiline,
    vi_mode,
    emacs_insert_mode,
    vi_insert_mode,
    has_focus
)
from prompt_toolkit.filters.cli import has_selection

from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.completion import (
    display_completions_like_readline,
)
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name

# check out this dict for debugging
# from prompt_toolkit.key_binding.bindings.named_commands import _readline_commands
from prompt_toolkit.key_binding.key_bindings import (
    merge_key_bindings,
    ConditionalKeyBindings,
)
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyPressEvent
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.selection import SelectionState

from IPython.core.getipython import get_ipython
from IPython.terminal.shortcuts import create_ipython_shortcuts


E = KeyPressEvent
insert_mode = vi_insert_mode | emacs_insert_mode


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app

# Conditions:


@Condition
def is_returnable():
    return get_app().current_buffer.is_returnable


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
def suggestion_available():
    app = get_app()
    return (
        app.current_buffer.suggestion is not None
        and app.current_buffer.document.is_cursor_at_the_end
    )


# *** Key Bindings: ***


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    # logger.debug('%s', dir(event))
    vi_state.input_mode = InputMode.NAVIGATION


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
    from prompt_toolkit.key_binding.bindings.auto_suggest import load_auto_suggest_bindings
    from prompt_toolkit.key_binding.bindings.cpr import load_cpr_bindings
    from prompt_toolkit.key_binding.bindings.emacs import (
        load_emacs_bindings,
        load_emacs_search_bindings,
    )
    from prompt_toolkit.key_binding.bindings.mouse import load_mouse_bindings
    from prompt_toolkit.key_binding.bindings.page_navigation import (
        load_page_navigation_bindings,
    )
    from prompt_toolkit.key_binding.bindings.vi import (
        load_vi_bindings,
        load_vi_search_bindings,
    )

    return [
        load_auto_suggest_bindings(),
        load_cpr_bindings(),
        load_emacs_bindings(),
        load_emacs_search_bindings(),
        load_vi_bindings(),
        load_vi_search_bindings(),
        load_mouse_bindings(),
        load_page_navigation_bindings(),
        create_ipython_shortcuts(get_ipython()),
        custom_key_bindings,
    ]


def add_bindings():
    registry = KeyBindings()

    handle = registry.add
    handle(Keys.ControlI)(display_completions_like_readline)

    # insert mode

    @handle("c-o", filter=insert_mode)
    def _(event: E) -> None:
        """
        Go into normal mode for one single action.
        """
        event.app.vi_state.temporary_navigation_mode = True


    handle("j", "k", filter=insert_mode)(switch_to_navigation_mode)

    handle("home")(get_by_name("beginning-of-line"))
    handle(Keys.ControlA, filter=insert_mode)(get_by_name("beginning-of-line"))

    handle("end")(get_by_name("end-of-line"))
    handle(Keys.ControlE, filter=insert_mode)(get_by_name("end-of-line"))

    # just snagged a new one from prompt_toolkit.key_binding.bindings.vi

    @handle("c-x", "c-l", filter=insert_mode)
    def _(event: E) -> None:
        """
        Pressing the ControlX - ControlL sequence in Vi mode does line
        completion based on the other lines in the document and the history.
        """
        event.current_buffer.start_history_lines_completion()

    # In navigation mode, pressing enter will always return the input.
    handle("enter", filter=vi_navigation_mode & is_returnable)(
        get_by_name("accept-line")
    )

    # In insert mode, also accept input when enter is pressed, and the buffer
    # has been marked as single line.
    handle("enter", filter=is_returnable & ~is_multiline)(get_by_name("accept-line"))

    @handle("enter", filter=~is_returnable & vi_navigation_mode)
    def _(event: E) -> None:
        """
        Go to the beginning of next line.
        """
        b = event.current_buffer
        b.cursor_down(count=event.arg)
        b.cursor_position += b.document.get_start_of_line_position(
            after_whitespace=True
        )

    # ** In navigation mode **
    # Shit this should get broken up into it's own function it's really
    # hard to navigate around
    # List of navigation commands: http://hea-www.harvard.edu/~fine/Tech/vi.html

    @handle("insert", filter=vi_navigation_mode)
    def _(event: E) -> None:
        """
        Pressing the Insert key.
        """
        event.app.vi_state.input_mode = InputMode.INSERT

    @handle("insert", filter=insert_mode)
    def _(event: E) -> None:
        """
        Pressing the Insert key.
        """
        event.app.vi_state.input_mode = InputMode.NAVIGATION

    @handle(Keys.Escape, "<")
    def beginning(event):
        """Move to the beginning of our recorded history."""
        event.current_buffer.cursor_position = 0

    @handle(Keys.Escape, ">")
    def end(event):
        """Move to the end."""
        event.current_buffer.cursor_position = len(event.current_buffer.text)

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
        """Right that wraps around in multiline."""
        if event.current_buffer.cursor_position + event.arg <= len(
            event.current_buffer.text
        ):
            event.current_buffer.cursor_position += event.arg

        if getattr(event.current_buffer.selection_state, "shift_arrow", False):
            event.current_buffer.selection_state = None

    @handle("up", filter=vi_navigation_mode)
    @handle("c-p", filter=vi_navigation_mode)
    def _(event: E) -> None:
        """
        Arrow up and ControlP in navigation mode go up.
        """
        event.current_buffer.auto_up(count=event.arg)

    @handle("k", filter=vi_navigation_mode)
    def _(event: E) -> None:
        """
        Go up, but if we enter a new history entry, move to the start of the
        line.
        """
        event.current_buffer.auto_up(
            count=event.arg, go_to_start_of_line_if_history_changes=True
        )

    @handle("down", filter=vi_navigation_mode)
    @handle("c-n", filter=vi_navigation_mode)
    def _(event: E) -> None:
        """
        Arrow down and Control-N in navigation mode.
        """
        event.current_buffer.auto_down(count=event.arg)

    @handle("j", filter=vi_navigation_mode)
    def _(event: E) -> None:
        """
        Go down, but if we enter a new history entry, go to the start of the line.
        """
        event.current_buffer.auto_down(
            count=event.arg, go_to_start_of_line_if_history_changes=True
        )

    @handle("backspace", filter=vi_navigation_mode)
    def _(event: E) -> None:
        """
        In navigation-mode, move cursor.
        """
        event.current_buffer.cursor_position += event.current_buffer.document.get_cursor_left_position(
            count=event.arg
        )

    @handle("c-n", filter=insert_mode)
    def _(event: E) -> None:
        b = event.current_buffer

        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=True)

    @handle("c-p", filter=insert_mode)
    def _(event: E) -> None:
        """
        Control-P: To previous completion.
        """
        b = event.current_buffer

        if b.complete_state:
            b.complete_previous()
        else:
            b.start_completion(select_last=True)

    @handle("c-g", filter=insert_mode)
    @handle("c-y", filter=insert_mode)
    def _(event: E) -> None:
        """
        Accept current completion.
        """
        event.current_buffer.complete_state = None

    @handle("c-e", filter=insert_mode)
    def _(event: E) -> None:
        """
        Cancel completion. Go back to originally typed text.
        """
        event.current_buffer.cancel_completion()

    # originally from basic_bindings

    handle("c-d", filter=has_text_before_cursor & insert_mode)(
        get_by_name("delete-char")
    )

    handle(Keys.ControlD, filter=ctrl_d_condition)(get_by_name("end-of-file"))

    @handle(Keys.ControlX, Keys.ControlE)
    def open_in_editor(event):
        # This is also firing on Alt-v?
        event.current_buffer.open_in_editor(handle_and_execute=True)

    def if_no_repeat(event: E) -> bool:
        """ Callable that returns True when the previous event was delivered to
        another handler. """
        return not event.is_repeat

    handle("c-up")(get_by_name("previous-history"))
    handle(Keys.ControlP)(get_by_name("previous-history"))
    handle("c-down")(get_by_name("next-history"))
    handle(Keys.ControlN)(get_by_name("next-history"))
    handle(Keys.ControlL)(get_by_name("clear-screen"))

    handle(Keys.ControlK, filter=insert_mode)(get_by_name("kill-line"))
    handle(Keys.ControlU, filter=insert_mode)(get_by_name("unix-line-discard"))
    handle("backspace", filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("backward-delete-char")
    )
    handle("delete", filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("delete-char")
    )
    handle("c-delete", filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("delete-char")
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

    ### Emacs:

    handle("c-a")(get_by_name("beginning-of-line"))
    handle("c-b")(get_by_name("backward-char"))
    handle("c-delete", filter=insert_mode)(get_by_name("kill-word"))
    handle("c-e")(get_by_name("end-of-line"))
    handle("c-f")(get_by_name("forward-char"))
    handle("c-left")(get_by_name("backward-word"))
    handle("c-right")(get_by_name("forward-word"))
    handle("c-x", "r", "y", filter=insert_mode)(get_by_name("yank"))
    handle("c-y", filter=insert_mode)(get_by_name("yank"))
    handle("c-_", save_before=(lambda e: False), filter=insert_mode)(
        get_by_name("undo")
    )

    handle("c-x", "c-u", save_before=(lambda e: False), filter=insert_mode)(
        get_by_name("undo")
    )

    handle("c-x", "(")(get_by_name("start-kbd-macro"))
    handle("c-x", ")")(get_by_name("end-kbd-macro"))
    handle("c-x", "e")(get_by_name("call-last-kbd-macro"))

    def character_search(buff, char, count):
        if count < 0:
            match = buff.document.find_backwards(
                char, in_current_line=True, count=-count
            )
        else:
            match = buff.document.find(char, in_current_line=True, count=count)

        if match is not None:
            buff.cursor_position += match

    @handle("c-]", Keys.Any)
    def _(event):
        " When Ctl-] + a character is pressed. go to that character. "
        # Also named 'character-search'
        character_search(event.current_buffer, event.data, event.arg)

    @handle("c-x", "c-x")
    def _(event):
        """
        Move cursor back and forth between the start and end of the current
        line.
        """
        buffer = event.current_buffer

        if buffer.document.is_cursor_at_the_end_of_line:
            buffer.cursor_position += buffer.document.get_start_of_line_position(
                after_whitespace=False
            )
        else:
            buffer.cursor_position += buffer.document.get_end_of_line_position()

    @handle("c-@")  # Control-space or Control-@
    def _(event):
        """
        Start of the selection (if the current buffer is not empty).
        """
        # Take the current cursor position as the start of this selection.
        buff = event.current_buffer
        if buff.text:
            buff.start_selection(selection_type=SelectionType.CHARACTERS)

    @handle("c-g", filter=has_selection)
    def _(event):
        """
        Control + G: Cancel completion menu and validation state.
        """
        event.current_buffer.complete_state = None
        event.current_buffer.validation_error = None

    @handle("c-g", filter=has_selection)
    def _(event):
        """
        Cancel selection.
        """
        event.current_buffer.exit_selection()

    @handle("c-w", filter=has_selection)
    @handle("c-x", "r", "k", filter=has_selection)
    def _(event):
        """
        Cut selected text.
        """
        data = event.current_buffer.cut_selection()
        event.app.clipboard.set_data(data)

    @handle("c-j")
    def _(event: E) -> None:
        r"""
        By default, handle \n as if it were a \r (enter).
        (It appears that some terminals send \n instead of \r when pressing
        enter. - at least the Linux subsystem for Windows.)
        """
        event.key_processor.feed(KeyPress(Keys.ControlM, "\r"), first=True)

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

    @handle(Keys.ControlZ)
    def suspend_to_bg(event: E) -> None:
        """
        By default, control-Z should literally insert Ctrl-Z.
        (Ansi Ctrl-Z, code 26 in MSDOS means End-Of-File.
        In a Python REPL for instance, it's possible to type
        Control-Z followed by enter to quit.)
        When the system bindings are loaded and suspend-to-background is
        supported, that will override this binding.
        """
        event.app.suspend_to_background()

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

    # End basic bindings

    # I added in some function keys

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

    @handle(Keys.ControlD, filter=ctrl_d_condition)
    def _(event):
        """Either delete a character or exit the application. TODO: this doesn't work"""
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "":
            event.app.exit()
        else:
            event.current_buffer.delete(count=event.arg)

    # apparently that function requires a positional parameter 'data'
    # fuckkkk if we ocmment it out we lose autocompletion
    @handle(Keys.Tab, filter=tab_insert_indent & insert_mode)
    def insert_indent(event):
        """If there are only whitespaces before current cursor position insert
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
            event.cli.current_buffer.insert_text("    ")

    @handle("(", filter=whitespace_or_bracket_after)
    def insert_right_parens(event):
        event.cli.current_buffer.insert_text("(")
        event.cli.current_buffer.insert_text(")", move_cursor=False)

    @handle(")")
    def overwrite_right_parens(event):
        buffer = event.cli.current_buffer
        if buffer.document.current_char == ")":
            buffer.cursor_position += 1
        else:
            buffer.insert_text(")")

    @handle("[", filter=whitespace_or_bracket_after)
    def insert_right_bracket(event):
        event.cli.current_buffer.insert_text("[")
        event.cli.current_buffer.insert_text("]", move_cursor=False)

    @handle("]")
    def overwrite_right_bracket(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "]":
            buffer.cursor_position += 1
        else:
            buffer.insert_text("]")

    @handle("{", filter=whitespace_or_bracket_after)
    def insert_right_brace(event):
        event.cli.current_buffer.insert_text("{")
        event.cli.current_buffer.insert_text("}", move_cursor=False)

    @handle("}")
    def overwrite_right_brace(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "}":
            buffer.cursor_position += 1
        else:
            buffer.insert_text("}")

    @handle("'")
    def insert_right_quote(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "'":
            buffer.cursor_position += 1
        elif whitespace_or_bracket_before() and whitespace_or_bracket_after():
            buffer.insert_text("'")
            buffer.insert_text("'", move_cursor=False)
        else:
            buffer.insert_text("'")

    @handle('"')
    def insert_right_double_quote(event):
        buffer = event.cli.current_buffer

        if buffer.document.current_char == '"':
            buffer.cursor_position += 1
        elif whitespace_or_bracket_before() and whitespace_or_bracket_after():
            buffer.insert_text('"')
            buffer.insert_text('"', move_cursor=False)
        else:
            buffer.insert_text('"')

    @handle(Keys.Backspace)
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

    handle(Keys.Any, filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("self-insert")
    )

    # autosuggest

    @handle("c-f", filter=suggestion_available)
    @handle("c-e", filter=suggestion_available)
    @handle("right", filter=suggestion_available)
    def _(event):
        " Accept suggestion. "
        b = event.current_buffer
        suggestion = b.suggestion

        if suggestion:
            b.insert_text(suggestion.text)

    # return ConditionalKeyBindings(registry, filter=buffer_has_focus)
    return registry

if __name__ == "__main__":

    _ip = get_ipython()
    if _ip is not None:
        _ip.pt_app.app.output.enable_bracketed_paste()
        bindings = add_bindings()
        extra_bindings = merge_key_bindings(get_key_bindings(bindings))
        _ip.pt_app.app.key_bindings = extra_bindings
