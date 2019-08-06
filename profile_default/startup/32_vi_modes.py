#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dynamically add keybindings to IPython.

====================================
Keybindings and Toggling Insert Mode
====================================

.. module:: 32_vi_modes
   :synopsis: Add extra keybindings to IPython.

:URL: https://ipython.readthedocs.io/en/stable/config/details.html#keyboard-shortcuts

Effectively adds :kbd:`j` :kbd:`k` as a way to switch from insert mode to
normal mode, or as :mod:`prompt_toolkit` calls it, "navigation mode".

Also displays how to integrate :mod:`prompt_toolkit` and :mod:`IPython`
together well.

Ultimately this module hopes to implementing Tim Pope's vim plugin *rsi* in
IPython.

Specifically it intends on adding the standard :mod:`readline` bindings
to Vim's insert mode.

.. todo:: Refactor everything as classes.

    This is quite hard to follow as is.


See Also
---------
:mod:`prompt_toolkit.key_binding.defaults` : str (path)
    Has all the named commands implemented here and possibly more.

---------------------

"""
import logging

from IPython import get_ipython
from IPython.terminal.shortcuts import create_ipython_shortcuts

from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode, ViNavigationMode
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
# commented out but we could refactor with Keys.Ctrl-a to avoid using strings
# for an enumerated data type
# from prompt_toolkit.keys import KEY_ALIASES, Keys
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.key_binding.bindings import named_commands, vi
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name

try:
    from ipykernel.zmqshell import ZMQInteractiveShell
except (ImportError,ModuleNotFoundError):
    ZMQInteractiveShell = None

from profile_default.util import module_log


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    # logger.debug('%s', dir(event))
    vi_state.input_mode = InputMode.NAVIGATION


def get_default_vim_bindings():
    """Adds 300 bindings to IPython! Merge any existing KeyBindings classes.

    Before we keep going we should figure out if we can use the + operator
    and just add the vi bindings that way.
    In addition, how do we add these instances of keybindings from the vi
    and emacs classes to our keybindings class?

    Just merge them and keep merging? Idk.

    Returns
    -------
    MergedKeys : :class:`~prompt_toolkit.key_bindings.MergedKeyBindings()`

    """
    return merge_key_bindings([
        vi.load_vi_bindings(),
        vi.load_vi_search_bindings()
    ])


def emacs_bindings():
    """Load emacs bindings in Vim's insert mode.

    """
    kb = KeyBindings()
    kb.add('c-a', filter=(insert_mode))(named_commands.beginning_of_line)
    kb.add('c-b', filter=(insert_mode))(named_commands.backward_char)
    kb.add('c-delete', filter=(insert_mode))(named_commands.kill_word)
    kb.add('c-e', filter=(insert_mode))(named_commands.end_of_line)
    kb.add('c-f', filter=(insert_mode))(named_commands.forward_char)
    kb.add('c-left', filter=(insert_mode))(named_commands.backward_word)
    kb.add('c-right', filter=(insert_mode))(named_commands.forward_word)
    kb.add('c-x', 'r', 'y', filter=(insert_mode))(named_commands.yank)
    kb.add('c-y', filter=(insert_mode))(named_commands.yank)
    # kb.add('c-o', filter=(insert_mode))(named_commands.operate-and-get-next)
    # kb.add('c-x', 'c-u', save_before=(lambda e: False), filter=insert_mode,
    # filter=(insert_mode)(named_commands.undo))
    return kb


def emacs_alt_bindings():
    """TODO: Docstring for emacs_alt_bindings.

    .. ipython::

        In [1]: timeit emacs_alt_bindings()
        762 µs ± 911 ns per loop (mean ± std. dev. of 7 runs, 1000 loops each)

    Returns
    -------
    kb : :class:`~prompt_toolkit.key_bindings.KeyBindings()`

    """
    kb = KeyBindings()
    kb.add('escape', 'b', filter=(insert_mode))(named_commands.backward_word)
    kb.add('escape', 'c', filter=(insert_mode))(named_commands.capitalize_word)
    kb.add('escape', 'd', filter=(insert_mode))(named_commands.kill_word)
    kb.add('escape', 'f', filter=(insert_mode))(named_commands.forward_word)
    kb.add('escape', 'l', filter=(insert_mode))(named_commands.downcase_word)
    kb.add('escape', 'u', filter=(insert_mode))(named_commands.uppercase_word)
    kb.add('escape', 'y', filter=(insert_mode))(named_commands.yank_pop)
    kb.add(
        'escape', 'backspace', filter=(insert_mode)
    )(named_commands.backward_kill_word)
    kb.add(
        'escape', '\\', filter=(insert_mode)
    )(named_commands.delete_horizontal_space)

    return kb


def base_keys(escape_keys=False):
    """Set up the easy ones."""
    kb = KeyBindings()

    ph = get_by_name('previous-history')
    nh = get_by_name('next-history')

    kb.add_binding(u'j', u'k', filter=(insert_mode))(switch_to_navigation_mode)
    kb.add_binding(
        'K', filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode())
    )(ph)

    kb.add_binding(
        'J', filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode())
    )(nh)

    if escape_keys:
        emacs_keys = merge_key_bindings([emacs_bindings(), emacs_alt_bindings()])
    else:
        emacs_keys = emacs_bindings()

    # actually let's load pt's vim keybindings first.
    # nope! merged key bindings class doesn't have the add_binding method!
    vim_keys = get_default_vim_bindings()

    rsi = merge_key_bindings([emacs_keys, vim_keys])

    return rsi


def main():
    """Begin initializing keybindings for `IPython`.

    This function delegates the extra bindings.

    Parameters
    ----------
    escape_keys : bool, Optional
        Whether to load :kbd:`Esc` or :kbd:`Alt` key bindings.

    Returns
    -------
    rsi : :class:`prompt_toolkit.key_bindings.KeyBindings()`
        Readline bindings in Vim 's insert mode.

    """
    almost_all_keys = base_keys(escape_keys=False)

    _ip = get_ipython()

    # IPython < 7.0
    if hasattr(_ip, 'pt_cli'):
        _ip.pt_cli.application.key_bindings_registry = merge_key_bindings([almost_all_keys, create_ipython_shortcuts(_ip)])
        RSI_LOGGER.info('Number of keybindings:'
                '{}:\t'.format(_ip.pt_cli.application.key_bindings_registry.bindings))
    # IPython >= 7.0
    elif hasattr(_ip, 'pt_app'):

        # Here's one that might blow your mind.
        if type(_ip.pt_app) == None:
            sys.exit()  # ran into this while running pytest.
            # If you start IPython from something like pytest i guess it starts
            # the machinery with a few parts missing...I don't know.

        _ip.pt_app.key_bindings = merge_key_bindings([almost_all_keys, create_ipython_shortcuts(_ip)])
        RSI_LOGGER.info('Number of keybindings {}:\t'.format(len(_ip.pt_app.key_bindings.bindings)))

    # Jupyter QTConsole
    elif isinstance(_ip, ZMQInteractiveShell):
        sys.exit()

    else:
        RSI_LOGGER.error('Is this being run in IPython?:\nType: %s ',
                          type(_ip), exc_info=1)


if __name__ == "__main__":
    insert_mode = (HasFocus(DEFAULT_BUFFER) & ViInsertMode())

    level = 10
    RSI_LOG = logging.getLogger(name='32_vi_modes')

    RSI_LOGGER = module_log.stream_logger(logger=RSI_LOG, log_level=level)

    main()
