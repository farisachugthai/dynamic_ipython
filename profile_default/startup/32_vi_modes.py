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

Fortunately for us, John implemented named commands from readline and made them easily
accessed through :ref:`prompt_toolkit.key_binding.bindings.named_commands.get_by_name`

As a result, K and J were rebound to "previous-history" and "next-history" while in
Vim normal mode.


"""
import logging

from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode
from prompt_toolkit.key_binding import  merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name

from IPython import get_ipython
from IPython.terminal.interactiveshell import create_ipython_shortcuts

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

    I genuinely didn't expect ``if get_attr(_ip, 'pt_app', None)`` to eval to ``None``.

    Below I posted the full implementation of when the keybindings are added in...
    but it's so late in the process that we need to know basically all the attributes
    of the class :class:`traitlets.Configurable`.

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
    """
    if shell is None:
        _ip = get_ipython()

    tmp_kb = create_ipython_shortcuts(_ip)
    # idk if i did this right but i'm hoping this captures all passed KeyBindings objects to that container
    OurRegistry, *OtherRegistries = args

    merged = merge_key_bindings(tmp_kb, OurRegistry, *OtherRegistries)
    return merged


if __name__ == "__main__":
    _ip = get_ipython()

    level = 10
    log = logging.getLogger(name=__name__)

    logger = module_log.stream_logger(log_level=level, logger=log)

    # uhhhh what do we do in the else case? do we restart IPython or build prompt_toolkit in the form we want?
    if getattr(_ip, 'pt_app', None):
        kb = _ip.pt_app.key_bindings
        kb.add_binding(
            u'c', u'k', filter=(HasFocus(DEFAULT_BUFFER)
                                & ViInsertMode()))(switch_to_navigation_mode)

    ph = get_by_name('previous-history')
    nh = get_by_name('next-history')

    registry.add_binding('K',
                         filter=(HasFocus(DEFAULT_BUFFER) &
                                 ViNavigationMode()))(ph)

    registry.add_binding('J',
                         filter=(HasFocus(DEFAULT_BUFFER) &
                                 ViNavigationMode()))(nh)
