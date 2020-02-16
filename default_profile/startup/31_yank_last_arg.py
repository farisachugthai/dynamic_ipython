r"""Add keybindings.
{{{
Slowly becoming where all my consolidated scripts for making prompt_toolkit's
handling of keypresses cohesive.

TODO: still need C-z
Tab doesn't start autocompletion when no letters have been typed in.
Damnit I lost C-d again.

However <CR> and <C-m> work as expected. haven't even tried navigation mode;
however, there's supposed to be ~500 key bindings so I'm excited.

.. warning::

    This is very experimental code.

Btw what is this?

Calling exit doesn't work?::

    In [2]: _ip.pt_app.app
    Out[2]: <prompt_toolkit.application.application.Application at 0x1f26c275250>

    In [3]: _ip.pt_app.app.exit()

    Exception                                 Traceback (most recent call last)
    <ipython-input-3-8964da7b84f6> in <module>
    ----> 1 _ip.pt_app.app.exit()
            global _ip.pt_app.app.exit = <bound method Application.exit of <prompt_toolkit.application.application.Application object at 0x000001F26C275250>>

    ~\scoop\apps\winpython\current\python-3.8.1.amd64\lib\site-packages\prompt_toolkit\application\application.py in exit(self=<prompt_toolkit.application.application.Application object>, result=None, exception=None, style='')
        771
        772         if self.future.done():
    --> 773             raise Exception(
            global Exception = undefined
        774                 'Return value already set. Application.exit() failed.')
        775

    Exception: Return value already set. Application.exit() failed.

}}}
"""
# {{{
# from collections import namedtuple
# import ctypes
# import functools
# from traceback import print_exception
import logging

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
    emacs_mode,
    vi_insert_mode,
    has_focus,
)
from prompt_toolkit.filters.cli import has_selection, ViInsertMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.completion import (
    display_completions_like_readline,
)
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
from prompt_toolkit.key_binding.bindings.scroll import scroll_page_down, scroll_page_up
from prompt_toolkit.key_binding.bindings.search import abort_search

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

from default_profile.startup import STARTUP_LOGGER
from default_profile.startup.ptoolkit import get_app

# }}}

logger = STARTUP_LOGGER.getChild('thirty-one')

E = KeyPressEvent
insert_mode = vi_insert_mode | emacs_insert_mode

# Conditions: {{{


@Condition
def is_returnable():
    return get_app().current_buffer.is_returnable


# is_returnable = Condition(lambda: get_app().current_buffer.is_returnable)


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
    if not beginning_of_line:
        return False
    if buffer_name == DEFAULT_BUFFER and not app.current_buffer.text:
        return True


# This is erroring...is it because its the only condition that requires an argument?
# So far I think so
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


@Condition
def suggestion_available():
    app = get_app()
    return (
        app.current_buffer.suggestion is not None
        and app.current_buffer.document.is_cursor_at_the_end
    )


@Condition
def has_selection():
    """
    Enable when the current buffer has a selection.
    """
    return bool(get_app().current_buffer.selection_state)


# }}}

# Not conditions: {{{


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


# }}}

# {{{


def get_key_bindings(custom_key_bindings=None):
    """Load key_bindings for the application and customize as necessary.

    Parameters
    ----------
    custom_key_bindings : KeyBindings
        The return value of the function in this module `add_bindings`.

    Notes
    ------
    .. warning::

        The ``__init__`` for `_MergedKeyBindings` features this.::

            def __init__(self, registries):
                assert all(isinstance(r, KeyBindingsBase) for r in registries)
                _Proxy.__init__(self)
                self.registries = registries

        As a result `None` can't be passed to `merge_key_bindings`.

    """
    from prompt_toolkit.key_binding.bindings.auto_suggest import (
        load_auto_suggest_bindings,
    )
    from prompt_toolkit.key_binding.defaults import load_key_bindings

    from prompt_toolkit.key_binding.bindings.page_navigation import (
        load_page_navigation_bindings,
    )

    kb = [
        create_ipython_shortcuts(get_ipython()),
        load_auto_suggest_bindings(),
        load_key_bindings(),
        load_page_navigation_bindings(),
    ]
    if custom_key_bindings is not None:
        kb.append(custom_key_bindings)
    merged = merge_key_bindings(kb)

    return merged  # }}}


def add_bindings():  # {{{
    registry = KeyBindings()

    handle = registry.add

    # basic: {{{
    handle("home")(get_by_name("beginning-of-line"))
    handle(Keys.ControlA, filter=insert_mode)(get_by_name("beginning-of-line"))

    handle("end")(get_by_name("end-of-line"))
    handle(Keys.ControlE, filter=insert_mode)(get_by_name("end-of-line"))

    handle(Keys.ControlA)(get_by_name("beginning-of-line"))
    handle(Keys.ControlB)(get_by_name("backward-char"))
    handle("c-delete", filter=insert_mode)(get_by_name("kill-word"))
    # Don't forget the filter because auto_completion is also gonna want this key
    handle(Keys.ControlE, filter=insert_mode)(get_by_name("end-of-line"))
    handle(Keys.ControlF)(get_by_name("forward-char"))
    handle("c-left")(get_by_name("backward-word"))
    handle("c-right")(get_by_name("forward-word"))

    handle(Keys.ControlX, "r", "y", filter=insert_mode)(get_by_name("yank"))

    handle(Keys.ControlY, filter=insert_mode)(get_by_name("yank"))
    handle(Keys.ControlUnderscore, save_before=(lambda e: False), filter=insert_mode)(
        get_by_name("undo")
    )

    handle(
        Keys.ControlX, Keys.ControlU, save_before=(lambda e: False), filter=insert_mode
    )(get_by_name("undo"))

    handle(Keys.ControlX, "(")(get_by_name("start-kbd-macro"))
    handle(Keys.ControlX, ")")(get_by_name("end-kbd-macro"))
    handle(Keys.ControlX, "e")(get_by_name("call-last-kbd-macro"))

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

    @handle(Keys.ControlX, Keys.ControlX)
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

    # }}}
    # End basic bindings

    # ** In navigation mode **: {{{
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

    @handle(Keys.Escape, "<", filter=vi_navigation_mode)
    def beginning(event):
        """Move to the beginning of our recorded history."""
        event.current_buffer.cursor_position = 0

    @handle(Keys.Escape, ">", filter=vi_navigation_mode)
    def end(event):
        """Move to the end."""
        event.current_buffer.cursor_position = len(event.current_buffer.text)

    @handle(Keys.Left, filter=beginning_of_line)
    def wrap_cursor_back(event):
        """Move cursor to end of previous line unless at beginning of
        document
        """
        b = event.cli.current_buffer
        b.cursor_up(count=1)
        relative_end_index = b.document.get_end_of_line_position()
        b.cursor_right(count=relative_end_index)

    @handle(Keys.Left)
    def left_multiline(event):
        """
        Left that wraps around in multiline.
        """
        if event.current_buffer.cursor_position - event.arg >= 0:
            event.current_buffer.cursor_position -= event.arg

        if getattr(event.current_buffer.selection_state, "shift_arrow", False):
            event.current_buffer.selection_state = None

    @handle(Keys.Right, filter=end_of_line)
    def wrap_cursor_forward(event):
        """Move cursor to beginning of next line unless at end of document"""
        b = event.cli.current_buffer
        relative_begin_index = b.document.get_start_of_line_position()
        b.cursor_left(count=abs(relative_begin_index))
        b.cursor_down(count=1)

    @handle(Keys.Right)
    def right_multiline(event):
        """Right that wraps around in multiline."""
        if event.current_buffer.cursor_position + event.arg <= len(
            event.current_buffer.text
        ):
            event.current_buffer.cursor_position += event.arg

        if getattr(event.current_buffer.selection_state, "shift_arrow", False):
            event.current_buffer.selection_state = None

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
        """In navigation-mode, move cursor."""
        event.current_buffer.cursor_position += event.current_buffer.document.get_cursor_left_position(
            count=event.arg
        )
        # }}}

    # vi insert mode: {{{

    # This'll be nice
    handle(Keys.ControlSpace, filter=insert_mode)(get_by_name("complete"))

    @handle(Keys.BackTab, filter=insert_mode)
    def insert_literal_tab(event):
        """ Insert literal tab on Shift+Tab instead of autocompleting """
        b = event.current_buffer
        if b.complete_state:
            b.complete_previous()
        else:
            event.cli.current_buffer.insert_text("    ")

    handle(Keys.ControlI)(display_completions_like_readline)

    @handle("c-o", filter=vi_insert_mode)
    def _(event: E) -> None:
        """
        Go into normal mode for one single action.
        """
        event.app.vi_state.temporary_navigation_mode = True

    handle("j", "k", filter=insert_mode)(switch_to_navigation_mode)


    # In insert mode, also accept input when enter is pressed, and the buffer
    # has been marked as single line.
    handle("enter", filter=is_returnable)(get_by_name("accept-line"))

    # why the literal fuck did i do this
    # @handle("")
    # def _(event: E) -> None:
    #     """
    #     Go to the beginning of next line.
    #     In navigation mode, pressing enter will always return the input.
    #     """
    #     b = event.current_buffer
    #     b.cursor_down(count=event.arg)
    #     b.cursor_position += b.document.get_start_of_line_position(
    #         after_whitespace=True
    #     )

    # just snagged a new one from prompt_toolkit.key_binding.bindings.vi

    @handle(Keys.ControlX, Keys.ControlL, filter=insert_mode)
    def _(event: E) -> None:
        """
        Pressing the ControlX - ControlL sequence in Vi mode does line
        completion based on the other lines in the document and the history.
        """
        event.current_buffer.start_history_lines_completion()

    @handle(Keys.ControlN, filter=insert_mode)
    def start_or_cycle_completions(event: E) -> None:
        b = event.current_buffer

        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=True)

    @handle(Keys.Tab, filter=insert_mode)
    def complete(event):
        b = event.current_buffer

        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=True)

    @handle(Keys.ControlX, Keys.ControlP, filter=insert_mode)
    def ctrlp(event):
        """Autocomplete things. Or if we already opened the completions go back."""
        b = event.current_buffer

        if b.complete_state:
            b.complete_previous()
        else:
            b.start_completion(select_last=True)


    @handle("up", filter=vi_navigation_mode)
    @handle("c-p", filter=vi_navigation_mode)
    @handle(Keys.ControlP, filter=insert_mode)
    def either_previous_completion_or_go_up(event: E) -> None:
        """Control-P: To previous completion.

        Otherwise, if we're in emacs mode go up a line or to the previous_history
        Shit so should we use auto_up?

        Arrow up and ControlP in navigation mode go up.
        """
        b = event.current_buffer

        if b.complete_state:
            b.complete_previous()
        else:
            event.current_buffer.auto_up(count=event.arg)
            # b.start_completion(select_last=True)
            # I feel like this should still be go up a line

    # @handle(Keys.ControlG, filter=insert_mode)
    # @handle(Keys.ControlY, filter=insert_mode)
    # def _(event: E) -> None:
    #     """Accept current completion."""
    #     event.current_buffer.complete_state = None

    # originally from basic_bindings

    @handle(Keys.ControlX, Keys.ControlE)
    def open_in_editor(event):
        # This is also firing on Alt-v?
        event.current_buffer.open_in_editor(handle_and_execute=True)

    def if_no_repeat(event: E) -> bool:
        """ Callable that returns True when the previous event was delivered to
        another handler. """
        return not event.is_repeat

    handle("c-up")(get_by_name("previous-history"))

    # So we have handlers for everything else right?
    handle(Keys.ControlP, filter=emacs_mode)(get_by_name("previous-history"))
    handle(Keys.ControlN, filter=emacs_mode)(get_by_name("next-history"))

    handle("c-down")(get_by_name("next-history"))
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
    handle(Keys.ControlW, filter=insert_mode)(get_by_name("unix-word-rubout"))

    # }}}

    # Has selection: {{{
    @handle("c-@")  # Control-space or Control-@
    def _(event):
        """
        Start of the selection (if the current buffer is not empty).
        """
        # Take the current cursor position as the start of this selection.
        buff = event.current_buffer
        if buff.text:
            buff.start_selection(selection_type=SelectionType.CHARACTERS)

    @handle(Keys.ControlG, filter=has_selection)
    def _(event):
        """
        Control + G: Cancel completion menu and validation state.
        """
        event.current_buffer.complete_state = None
        event.current_buffer.validation_error = None

    @handle(Keys.ControlG, filter=has_selection)
    def _(event):
        """
        Cancel selection.
        """
        event.current_buffer.exit_selection()

    @handle(Keys.ControlW, filter=has_selection)
    @handle(Keys.ControlX, "r", "k", filter=has_selection)
    def _(event):
        """
        Cut selected text.
        """
        data = event.current_buffer.cut_selection()
        event.app.clipboard.set_data(data)

    @handle(Keys.ControlJ)
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

    # }}}

    # Global bindings.: {{{

    # No filters i want this recognized all the time.
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

    # }}}

    # I added in some function keys: {{{

    @handle(Keys.F4)
    def toggle_editing_mode(event):
        """Toggle between Vi and Emacs mode.

        See Also
        --------
        `34_bottom_toolbar`
            Utilized for this purpose.
        """
        event.app.editing_mode = not event.app.editing_mode == "vi"
        event.app.key_bindings._update_cache()

    handle(Keys.Escape, Keys.ControlJ)(toggle_editing_mode)

    @handle(Keys.F6)
    def _(event):
        """
        Enable/Disable paste mode.
        """
        event.app.paste_mode = not event.app.paste_mode

        """
        Pressing Ctrl-C will exit the user interface.
        Setting a return value means: quit the event loop that drives the user
        interface and return this value from the `Application.run()` call.
        """

    @handle(Keys.ControlD, filter=ctrl_d_condition)
    def _(event):
        """Either delete a character or exit the application. TODO: this doesn't work"""
        buffer = event.cli.current_buffer

        if buffer.document.current_char == "":
            event.app.exit()
        else:
            event.current_buffer.delete(count=event.arg)

    handle("c-d", filter=has_text_before_cursor & insert_mode)(
        get_by_name("delete-char")
    )

    # this doesn't do what you'd expect.
    # handle(Keys.ControlD)(get_by_name("end-of-file"))

    # @handle(Keys.ControlD)
    # def exit_app(event):
    # HE CATCHES RUNTIMEERROR WHAT THE FUCK
    # raise RuntimeError
    # ugh why isn't this working :(
    # event.app.exit(result=False)
    # I'm actually not sure why that isn't working. It raises an error because
    # a concurrent.future.Future object already completed. However we can do
    # this on te IPython side and it'll work easily
    @handle(Keys.ControlD, filter=insert_mode)
    def exit_app(event):
        """Invoke the |ip| method *ask_exit*."""
        if get_ipython() is not None:
            return get_ipython().ask_exit()

    # @handle(Keys.ControlD, filter=vi_navigation_mode)(scroll_page_down)
    # todo: gotta do this for c-d in navigation mode too
    # @handle(Keys.ControlF, filter=vi_navigation_mode)(scroll_page_down)

    # }}}

    # matchit: {{{

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

    # }}}

    # autosuggest: {{{

    @handle("c-f", filter=suggestion_available)
    @handle("c-e", filter=suggestion_available)
    @handle("right", filter=suggestion_available)
    def _(event):
        " Accept suggestion. "
        b = event.current_buffer
        suggestion = b.suggestion

        if suggestion:
            b.insert_text(suggestion.text)

    @handle(Keys.ControlM, filter=is_searching())
    @handle(Keys.ControlJ, filter=is_searching())
    def accept_search(event):
        search.accept_search()

    # page navigation *because  why are these conditional on editing mode*
    handle("pagedown")(scroll_page_down)
    handle("pageup")(scroll_page_up)

    handle(Keys.Any, filter=insert_mode, save_before=if_no_repeat)(
        get_by_name("self-insert")
    )
    # }}}
    # return ConditionalKeyBindings(registry, filter=buffer_has_focus)

    return registry  # }}}


if __name__ == "__main__":

    _ip = get_ipython()
    if _ip is not None:
        # bindings = add_bindings()
        # Let's see if i can't get a more consistent result without my bindings
        extra_bindings = get_key_bindings(add_bindings())
        _ip.pt_app.app.key_bindings = extra_bindings

        _ip.pt_app.app.output.enable_bracketed_paste()

# Vim: set fdm=marker fdls=0:
