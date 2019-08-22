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
from pathlib import Path

from IPython import get_ipython
from IPython.terminal.shortcuts import create_ipython_shortcuts

from prompt_toolkit import PromptSession
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode, ViNavigationMode

# Might not be a bad idea to add
# from prompt_toolkit.filters.base import Condition

from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.bindings import named_commands, vi

# we could refactor all bindings with Keys.Ctrl-a to avoid using strings
# for an enumerated data type
# from prompt_toolkit.keys import KEY_ALIASES, Keys

from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.key_binding.bindings import named_commands, vi
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name

from profile_default.util import module_log

class AddRLBindings:
    """A class to add readline bindings independently of prompt toolkit."""

    def __init__(self):
        """Initialize the class and check for readline."""
        try:
            import readline
        except (ImportError, ModuleNotFoundError):
            # hmmm what do we fall back to?
            readline = None
        else:
            readline.read_init_file(str(self.get_home().joinpath('.inputrc')))

    @staticmethod
    def get_home(self):
        """Return the user's home dir."""
        return Path(home)


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

    Returns
    -------
    MergedKeys : :class:`prompt_toolkit.key_bindings.MergedKeyBindings`

    """
    return merge_key_bindings(
        [vi.load_vi_bindings(),
         vi.load_vi_search_bindings()])


def emacs_bindings():
    """Load emacs bindings in Vim's insert mode."""
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

        In [#]: from profile_default.startup import vi_mode_keybindings
        In [#]: %timeit vi_mode_keybindings.emacs_alt_bindings()
        762 µs ± 911 ns per loop (mean ± std. dev. of 7 runs, 1000 loops each)

    Returns
    -------
    kb : :class:`prompt_toolkit.key_bindings.KeyBindings()`
        Extra Emacs keys for the console.

    """
    kb = KeyBindings()
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

    return kb


def base_keys(escape_keys=False):
    """Set up the easy ones."""
    kb = KeyBindings()

    ph = get_by_name('previous-history')
    nh = get_by_name('next-history')

    kb.add_binding(u'j', u'k', filter=(insert_mode))(switch_to_navigation_mode)
    kb.add_binding('K',
                   filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode()))(ph)

    kb.add_binding('J',
                   filter=(HasFocus(DEFAULT_BUFFER) & ViNavigationMode()))(nh)

    if escape_keys:
        emacs_keys = merge_key_bindings(
            [emacs_bindings(), emacs_alt_bindings()])
    else:
        emacs_keys = emacs_bindings()

    # actually let's load pt's vim keybindings first.
    # nope! merged key bindings class doesn't have the add_binding method!
    vim_keys = get_default_vim_bindings()

    rsi = merge_key_bindings([emacs_keys, vim_keys])

    return rsi


def merge_ipython_rsi_kb(_ip=None):
    """This really needs to be redone so I don't have to keep passing around this global not global _ip."""
    # IPython < 7.0
    if hasattr(_ip, 'pt_cli'):
        _ip.pt_cli.application.key_bindings_registry = merge_key_bindings(
            [almost_all_keys, create_ipython_shortcuts(_ip)])
        RSI_LOGGER.info(
            'Number of keybindings:'
            '{}:\t'.format(
                _ip.pt_cli.application.key_bindings_registry.bindings))
    # IPython >= 7.0
    elif hasattr(_ip, 'pt_app'):

        # Here's one that might blow your mind.
        if type(_ip.pt_app) == None:
            sys.exit()  # ran into this while running pytest.
            # If you start IPython from something like pytest i guess it starts
            # the machinery with a few parts missing...I don't know.

        _ip.pt_app.key_bindings = merge_key_bindings(
            [almost_all_keys, create_ipython_shortcuts(_ip)])
        RSI_LOGGER.info('Number of keybindings {}:\t'.format(
            len(_ip.pt_app.key_bindings.bindings)))

    else:
        try:
            from ipykernel.zmqshell import ZMQInteractiveShell
        except (ImportError, ModuleNotFoundError):
            ZMQInteractiveShell = None
            RSI_LOGGER.error('Is this being run in IPython?:\nType: %s ',
                             type(_ip),
                             exc_info=1)
        else:
            # Jupyter QTConsole
            if isinstance(_ip, ZMQInteractiveShell):
                sys.exit()

    return _ip


def main():
    """Begin initializing keybindings for `IPython`.

    This function delegates the extra bindings.

    Here's the super long init signature from
    :class:`prompt_toolkit.PromptSession`.:

        \_\_init\_\_(self, message, multiline, wrap_lines, is_password, vi_mode,
        editing_mode, complete_while_typing, validate_while_typing,
        enable_history_search, search_ignore_case, lexer, enable_system_prompt,
        enable_suspend, enable_open_in_editor, validator, completer,
        complete_in_thread, reserve_space_for_menu, complete_style, auto_suggest,
        style, style_transformation, swap_light_and_dark_colors, color_depth,
        include_default_pygments_style, history, clipboard, prompt_continuation,
        rprompt, bottom_toolbar, mouse_support, input_processors, key_bindings,
        erase_when_done, tempfile_suffix, inputhook, refresh_interval, input,
        output)


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

    # _ip = merge_ipython_rsi_kb(_ip)  # TODO: ugh
    kb = base_keys()

    _ip.pt_app = PromptSession(
        complete_while_typing=True,
        editing_mode=getattr(EditingMode, _ip.editing_mode.upper()),
        bottom_toolbar=None,  # todo
        mouse_support=_ip.mouse_support,
        complete_style=_ip.pt_complete_style,
        inputhook=_ip.inputhook,
        color_depth=_ip.color_depth,
        key_bindings=kb,
        style=_ip.style)
    return _ip


if __name__ == "__main__":
    insert_mode = (HasFocus(DEFAULT_BUFFER) & ViInsertMode())

    RSI_LOGGER = module_log.stream_logger(logger="RSI", log_level=30)
    # So this hijacks the event loop and jams everything...
    # shell = main()

    try:
        import readline
    except (ImportError, ModuleNotFoundError):
        readline = None

    if hasattr(readline, 'read_init_file'):
        readline.read_init_file(
            os.path.expanduser(os.path.join('~', '.inputrc')))

    AddRLBindings()
