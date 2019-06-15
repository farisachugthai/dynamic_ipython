#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dynamically add keybindings to IPython. Strive to implementing Tim Pope's rsi plugin in IPython.

====================================
Keybindings and Toggling Insert Mode
====================================

.. module:: `32_vi_modes`

.. hope that doesn't crash the interpreter!

Effectively adds :kbd:`j` :kbd:`k` as a way to switch from insert mode to
normal mode, or as :mod:`prompt_toolkit` calls it, "navigation mode".

Also displays how to integrate :mod:`prompt_toolkit` and :mod:`IPython`
together well.

:URL: https://ipython.readthedocs.io/en/stable/config/details.html#keyboard-shortcuts

.. todo:: Add one in for :kbd:`C-M-j` to go to Emacs mode?


Original KeyBindings
====================

An initial concern may be that while dynamically bindings keys to the namespace,
one may accidentally delete all the keybindings provided by IPython.

This can be prevented by merging them in.

They're initialized through :func:`IPython.terminal.interactiveshell.create_ipython_shortcuts()`.
We can save those to a temporary :class:`prompt_toolkit.key_bindings.KeyBindings()` instance, and then
use the function :func:`prompt_toolkit.key_binding.merge_key_bindings()`


Readline Bindings
=================

Fortunately for us, John implemented named commands from readline and
made them easily accessible through
:ref:`prompt_toolkit.key_binding.bindings.named_commands.get_by_name`.

As a result, K and J were rebound to "previous-history" and "next-history"
while in Vim normal mode. However, very little is bound by default.

.. ipython::

    In [13]: _ip.pt_app.key_bindings.bindings
    Out[13]:
    [_Binding(keys=('c-m',), handler=<function newline_or_execute_outer.<locals>.newline_or_execute at 0x7c2c76f840>),
     _Binding(keys=('c-\\',), handler=<function force_exit at 0x7c2c7e51e0>),
     _Binding(keys=('c-p',), handler=<function previous_history_or_previous_completion at 0x7c2c7dee18>),
     _Binding(keys=('c-n',), handler=<function next_history_or_next_completion at 0x7c2c7deea0>),
     _Binding(keys=('c-g',), handler=<function dismiss_completion at 0x7c2c7def28>),
     _Binding(keys=('c-c',), handler=<function reset_buffer at 0x7c2c7e5048>),
     _Binding(keys=('c-c',), handler=<function reset_search_buffer at 0x7c2c7e50d0>),
     _Binding(keys=('c-z',), handler=<function suspend_to_bg at 0x7c2c7e5158>),
     _Binding(keys=('c-i',), handler=<function indent_buffer at 0x7c2c7e5268>),
     _Binding(keys=('c-o',), handler=<function newline_autoindent_outer.<locals>.newline_autoindent at 0x7c2c671400>),                                                                               _Binding(keys=('f2',), handler=<function open_input_in_editor at 0x7c2c7e5400>),
     _Binding(keys=('j', 'k'), handler=<function switch_to_navigation_mode at 0x7c2bd03c80>),
     _Binding(keys=('K',), handler=<function previous_history at 0x7c2d9d76a8>),
     _Binding(keys=('J',), handler=<function next_history at 0x7c2d9d7730>)]

That leaves a LOT to work with in terms of all the functions defined in
:ref:`prompt_toolkit.key_binding.bindings.default`.

Example Usage
==============

From the `source code`_:

.. ipython:: python

    from prompt_toolkit.keybinding import KeyBinding
    kb = KeyBindings()

    @kb.add('c-t')
    def _(event):
        print('Control-T pressed')

    @kb.add('c-a', 'c-b')
    def _(event):
        print('Control-A pressed, followed by Control-B')

    @kb.add('c-x', filter=is_searching)
    def _(event):
        print('Control-X pressed')  # Works only if we are searching.


.. _source-code: https://python-prompt-toolkit.readthedocs.io/en/stable/pages/reference.html#module-prompt_toolkit.key_binding


"""
import logging

from IPython import get_ipython
from IPython.terminal.interactiveshell import create_ipython_shortcuts
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode, ViNavigationMode
from prompt_toolkit.key_binding import merge_key_bindings
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
from prompt_toolkit.key_binding.vi_state import InputMode

from profile_default.util import module_log


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    logger.debug('%s', dir(event))
    vi_state.input_mode = InputMode.NAVIGATION


def original_bindings(*args, shell=None):
    """Merge in the old keybindings with ours.

    I genuinely didn't expect ``if get_attr(_ip, 'pt_app', None)`` to
    eval to ``None``.

    Below I posted the full implementation of when the keybindings are
    added in... but it's so late in the process that we need to know
    basically all the attributes of the class :class:`traitlets.Configurable`.

    Parameters
    ----------
    _ip : |ip|
        Global IPython instance

    Returns
    -------
    merged_keybindings : :class:`prompt_toolkit.key_bindings.MergedKeyBindings()`
        Merged keybindings.

    See Also
    --------
    :func:`~IPython.terminal.interactiveshell.create_ipython_shortcuts()`
        Where the shortcuts are added.

    Examples
    --------
    ::

       def init_prompt_toolkit_cli(self):
        if self.simple_prompt:
            # Fall back to plain non-interactive output for tests.
            # This is very limited.
            def prompt():
                prompt_text = "".join(x[1] for x in self.prompts.in_prompt_tokens())
                lines = [input(prompt_text)]
                prompt_continuation = "".join(x[1] for x in self.prompts.continuation_prompt_tokens())
                while self.check_complete('\n'.join(lines))[0] == 'incomplete':
                    lines.append( input(prompt_continuation) )
                return '\n'.join(lines)
            self.prompt_for_code = prompt
            return

        # Set up keyboard shortcuts
        key_bindings = create_ipython_shortcuts(self)

        # Pre-populate history from IPython's history database
        history = InMemoryHistory()
        last_cell = u""
        for __, ___, cell in self.history_manager.get_tail(self.history_load_length,
                                                        include_latest=True):
            # Ignore blank lines and consecutive duplicates
            cell = cell.rstrip()
            if cell and (cell != last_cell):
                history.append_string(cell)
                last_cell = cell

        self._style = self._make_style_from_name_or_cls(self.highlighting_style)
        self.style = DynamicStyle(lambda: self._style)

        editing_mode = getattr(EditingMode, self.editing_mode.upper())

        self.pt_app = PromptSession(
                            editing_mode=editing_mode,
                            key_bindings=key_bindings,
                            history=history,
                            completer=IPythonPTCompleter(shell=self),
                            enable_history_search = self.enable_history_search,
                            style=self.style,
                            include_default_pygments_style=False,
                            mouse_support=self.mouse_support,
                            enable_open_in_editor=self.extra_open_editor_shortcuts,
                            color_depth=self.color_depth,
                            **self._extra_prompt_options())

    That is so many mixins and traits oh my god.

    """
    if shell is None:
        _ip = get_ipython()

    tmp_kb = create_ipython_shortcuts(_ip)
    # idk if i did this right but i'm hoping this captures all passed KeyBindings objects to that container
    OurRegistry, *OtherRegistries = args

    merged = merge_key_bindings(tmp_kb, OurRegistry, *OtherRegistries)
    return merged


def main(_ip=None):
    """Begin initializing keybindings for IPython.

    .. todo::

        Add all the emacs keys to Vi insert mode.

    .. code-block::

        from prompt_toolkit.application.current import get_app
        from prompt_toolkit.buffer import Buffer, SelectionType, indent, unindent
        from prompt_toolkit.completion import CompleteEvent
        from prompt_toolkit.filters import (
            Condition,
            emacs_insert_mode,
            emacs_mode,
            has_arg,
            has_selection,
            is_multiline,
            is_read_only,
            vi_search_direction_reversed,
        )
        from prompt_toolkit.key_binding.key_processor import KeyPressEvent
        from prompt_toolkit.keys import Keys

        from ..key_bindings import ConditionalKeyBindings, KeyBindings, KeyBindingsBase
        from .named_commands import get_by_name

        E = KeyPressEvent

        def load_emacs_bindings() -> KeyBindingsBase:
            Some e-macs extensions.
            # Overview of Readline emacs commands:
            # http://www.catonmat.net/download/readline-emacs-editing-mode-cheat-sheet.pdf
            key_bindings = KeyBindings()
            handle = key_bindings.add

            insert_mode = emacs_insert_mode

            @handle('escape')
            def _(event: E) -> None:
                By default, ignore escape key.
                (If we don't put this here, and Esc is followed by a key which sequence
                is not handled, we'll insert an Escape character in the input stream.
                Something we don't want and happens to easily in emacs mode.
                Further, people can always use ControlQ to do a quoted insert.)
                pass

            handle('c-a')(get_by_name('beginning-of-line'))
            handle('c-b')(get_by_name('backward-char'))
            handle('c-delete', filter=insert_mode)(get_by_name('kill-word'))
            handle('c-e')(get_by_name('end-of-line'))
            handle('c-f')(get_by_name('forward-char'))
            handle('c-left')(get_by_name('backward-word'))
            handle('c-right')(get_by_name('forward-word'))
            handle('c-x', 'r', 'y', filter=insert_mode)(get_by_name('yank'))
            handle('c-y', filter=insert_mode)(get_by_name('yank'))
            handle('escape', 'b')(get_by_name('backward-word'))
            handle('escape', 'c', filter=insert_mode)(get_by_name('capitalize-word'))
            handle('escape', 'd', filter=insert_mode)(get_by_name('kill-word'))
            handle('escape', 'f')(get_by_name('forward-word'))
            handle('escape', 'l', filter=insert_mode)(get_by_name('downcase-word'))
            handle('escape', 'u', filter=insert_mode)(get_by_name('uppercase-word'))
            handle('escape', 'y', filter=insert_mode)(get_by_name('yank-pop'))
            handle('escape', 'backspace', filter=insert_mode)(get_by_name('backward-kill-word'))
            handle('escape', '\\', filter=insert_mode)(get_by_name('delete-horizontal-space'))

    Oh poop. I just realized. Instead of doing that, can we just call this function?
    :ref:`prompt_toolkit.key_binding.defaults.load_key_bindings()` and merge in the
    Emacs insert mode ones?

    Parameters
    ----------
    _ip : |ip|
        Global IPython instance.

    """
    # uhhhh what do we do in the else case? do we restart IPython or build prompt_toolkit in the form we want?
    if getattr(_ip, 'pt_app', None):
        kb = _ip.pt_app.key_bindings
        kb.add_binding(
            u'j', u'k', filter=(HasFocus(DEFAULT_BUFFER)
                                & ViInsertMode()))(switch_to_navigation_mode)

    ph = get_by_name('previous-history')
    nh = get_by_name('next-history')

    kb.add_binding('K', filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode()))(ph)

    kb.add_binding('J', filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode()))(nh)

    return kb


if __name__ == "__main__":
    _ip = get_ipython()

    level = 10
    log = logging.getLogger(name=__name__)

    logger = module_log.stream_logger(log_level=level, logger=log)

    keybindings = main(_ip)
    # how do we bind them back?
