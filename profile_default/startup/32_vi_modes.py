#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add a keybinding to IPython.

====================================
Keybindings and Toggling Insert Mode
====================================

Effectively adds :kbd:`j` :kbd:`k` as a way to switch from insert mode to
normal mode, or as :mod:`prompt_toolkit` calls it, "navigation mode".

Also displays how to integrate :mod:`prompt_toolkit` and :mod:`IPython`
together well.

:URL: https://ipython.readthedocs.io/en/stable/config/details.html#keyboard-shortcuts

.. todo:: Add one in for :kbd:`C-M-j` to go to Emacs mode?

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
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.vi_state import InputMode
from IPython import get_ipython

from profile_default.util import module_log


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    logger.debug('%s', dir(event))
    vi_state.input_mode = InputMode.NAVIGATION


def check_defaults():
    """What are the default keybindings we have here?

    Err I suppose I should say what does Prompt Toolkit export by default
    because I'm not 100% sure that ip imports everything or doesn't modify
    anything along the way.

    Probably gonna need to noqa something since the code isn't accessed as is.

    May 23, 2019:

        To my knowledge the keybindings you have available is every single
        one that prompt_toolkit ships with.

    .. code-block:: python3

        __all__ = [
            'load_key_bindings',
        ]


        def load_key_bindings():
            # Create a KeyBindings object that contains the default key bindings.
            all_bindings = merge_key_bindings([
                # Load basic bindings.
                load_basic_bindings(),

                # Load emacs bindings.
                load_emacs_bindings(),
                load_emacs_search_bindings(),

                # Load Vi bindings.
                load_vi_bindings(),
                load_vi_search_bindings(),
            ])

            return merge_key_bindings([
                # Make sure that the above key bindings are only active if the
                # currently focused control is a `BufferControl`. For other controls, we
                # don't want these key bindings to intervene. (This would break "ptterm"
                # for instance, which handles 'Keys.Any' in the user control itself.)
                ConditionalKeyBindings(all_bindings, buffer_has_focus),

                # Active, even when no buffer has been focused.
                load_mouse_bindings(),
                load_cpr_bindings(),
            ])

    That's literally everything. IPython chooses to add their own stuff
    during IPython.terminal.ptutil.create_ipython_shortcuts but if you
    choose to create your own registry then you get access to everything.

    It might not be hard to bind to if we do it the same way we did with
    that one pathlib.Path class.

    Literally::

        from IPython import get_ipython
        from prompt_toolkit.key_binding import merge_key_bindings, KeyBindings
        from prompt_toolkit.key_binding.defaults import load_key_bindings

        class KeyBindingsManager:

            def __init__(self, shell=None):
                if _ip is None:
                    _ip = get_ipython()
                self.registry = KeyBindings

    Once the user initializes that class, then your :class:`KeyBindings`
    statement in the `__init__` func was execute and you'll have access
    to everything. Cool!

    """
    registry = load_key_bindings()
    return registry.key_bindings


if __name__ == "__main__":
    _ip = get_ipython()

    level = 10
    log = logging.getLogger(name=__name__)

    logger = module_log.stream_logger(log_level=level, logger=log)

    if getattr(_ip, 'pt_app', None):
        kb = _ip.pt_app.key_bindings
        kb.add_binding(
            u'j', u'k', filter=(HasFocus(DEFAULT_BUFFER)
                                & ViInsertMode()))(switch_to_navigation_mode)
