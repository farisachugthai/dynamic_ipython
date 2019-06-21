#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dynamically add keybindings to IPython.

====================================
Keybindings and Toggling Insert Mode
====================================

.. module:: `32_vi_modes`

:URL: https://ipython.readthedocs.io/en/stable/config/details.html#keyboard-shortcuts

Effectively adds :kbd:`j` :kbd:`k` as a way to switch from insert mode to
normal mode, or as :mod:`prompt_toolkit` calls it, "navigation mode".

Also displays how to integrate :mod:`prompt_toolkit` and :mod:`IPython`
together well.

Ultimately this module hopes to implementing Tim Pope's rsi plugin in IPython.

Original KeyBindings
====================

They're initialized through
:func:`IPython.terminal.interactiveshell.create_ipython_shortcuts()`.
We can save those to a temporary :class:`prompt_toolkit.key_bindings.KeyBindings()`
instance, and then use the function
:func:`prompt_toolkit.key_binding.merge_key_bindings()`


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
     _Binding(keys=('c-o',), handler=<function newline_autoindent_outer.<locals>.newline_autoindent at 0x7c2c671400>),
     _Binding(keys=('f2',), handler=<function open_input_in_editor at 0x7c2c7e5400>),
     _Binding(keys=('j', 'k'), handler=<function switch_to_navigation_mode at 0x7c2bd03c80>),
     _Binding(keys=('K',), handler=<function previous_history at 0x7c2d9d76a8>),
     _Binding(keys=('J',), handler=<function next_history at 0x7c2d9d7730>)]

That leaves a LOT to work with in terms of all the functions defined in
:ref:`prompt_toolkit.key_binding.bindings.default`.


---------------------

Before we begin defining functions:

See Also
---------
_ip.pt_app.layout.current_buffer : :class:`prompt_toolkit.application.Buffer`
    Has all the named commands implemented here and possibly more.

"""
import logging

from IPython import get_ipython
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode, ViNavigationMode
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.key_binding.bindings import named_commands
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name

from profile_default.util import module_log


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    logger.debug('%s', dir(event))
    vi_state.input_mode = InputMode.NAVIGATION


def main(_ip=None):
    """Begin initializing keybindings for IPython.

    Here's a *slightly truncated version of the prompt_toolkit implementation for Emacs bindings.
    Note that the escape key is ignored, warranting the reimplementation rather than just
    importing John's work.::

        def load_emacs_bindings() -> KeyBindingsBase:
            Some e-macs extensions.
            # Overview of Readline emacs commands:
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


    Parameters
    ----------
    _ip : |ip|
        Global IPython instance.

    """
    # uhhhh what do we do in the else case? do we restart IPython or build prompt_toolkit in the form we want?
    if getattr(_ip, 'pt_app', None):
        kb = _ip.pt_app.key_bindings
    else:
        kb = KeyBindings()

    insert_mode = (HasFocus(DEFAULT_BUFFER) & ViInsertMode())

    # kb.add_binding(keys=(u'j', u'k'), filter=(insert_mode),
    # handler=(switch_to_navigation_mode))
    # fuck assert not kwargs is an expression in this so we can't use that but I hope it clarifies the format!
    ph = get_by_name('previous-history')
    nh = get_by_name('next-history')

    # kb.add_binding((u'j', u'k'), filter=(insert_mode)(switch_to_navigation_mode))
    kb.add_binding('K',
                   filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode()))(ph)

    kb.add_binding('J',
                   filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode()))(nh)

    # 06/15/2019: Got it.
    kb.add('c-a', filter=(insert_mode))(named_commands.beginning_of_line)
    # did you know that C-a won't work? Odd.
    kb.add('c-b', filter=(insert_mode))(named_commands.backward_char)
    kb.add('c-d', filter=(insert_mode))(named_commands.delete_char)
    kb.add('c-delete', filter=(insert_mode))(named_commands.kill_word)
    kb.add('c-e', filter=(insert_mode))(named_commands.end_of_line)
    kb.add('c-f', filter=(insert_mode))(named_commands.forward_char)
    kb.add('c-left', filter=(insert_mode))(named_commands.backward_word)
    kb.add('c-right', filter=(insert_mode))(named_commands.forward_word)
    kb.add('c-x', 'r', 'y', filter=(insert_mode))(named_commands.yank)
    kb.add('c-y', filter=(insert_mode))(named_commands.yank)
    kb.add('escape', 'b', filter=(insert_mode))(named_commands.backward_word)
    kb.add('escape', 'c', filter=(insert_mode))(named_commands.capitalize_word)
    kb.add('escape', 'd', filter=(insert_mode))(named_commands.kill_word)
    kb.add('escape', 'f', filter=(insert_mode))(named_commands.forward_word)
    kb.add('escape', 'l', filter=(insert_mode))(named_commands.downcase_word)
    kb.add('escape', 'u', filter=(insert_mode))(named_commands.uppercase_word)
    kb.add('escape', 'y', filter=(insert_mode))(named_commands.yank_pop)
    kb.add('escape', 'backspace',
           filter=(insert_mode))(named_commands.backward_kill_word)
    kb.add('escape', '\\',
           filter=(insert_mode))(named_commands.delete_horizontal_space)

    # how do i modify ones with preexisting filters?
    # i deleted a bunch of the insert_mode ones off but idk what to do about
    # others

    # kb.add('c-_', save_before=(lambda e: False), filter=insert_mode, filter=(insert_mode)(
    #     named_commands.undo))

    # kb.add('c-x', 'c-u', save_before=(lambda e: False), filter=insert_mode, filter=(insert_mode)(
    #     named_commands.undo))

    # kb.add('escape', '<', filter= ~has_selection, filter=(insert_mode)(named_commands.beginning-of-history))
    # kb.add('escape', '>', filter= ~has_selection, filter=(insert_mode)(named_commands.end-of-history))

    # kb.add('escape', '.',  filter=(insert_mode)(named_commands.yank-last-arg))
    # kb.add('escape', '_',  filter=(insert_mode)(named_commands.yank-last-arg))
    # kb.add('escape', 'c-y', filter=(insert_mode)(named_commands.yank-nth-arg))
    # kb.add('escape', '#', filter=(insert_mode)(named_commands.insert-comment))
    # kb.add('c-o', filter=(insert_mode)(named_commands.operate-and-get-next))

    return kb


if __name__ == "__main__":
    _ip = get_ipython()

    level = 10
    log = logging.getLogger(name=__name__)

    logger = module_log.stream_logger(log_level=level, logger=log)

    keybindings = main(_ip)
    # how do we bind them back?
