#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add a keybinding to IPython.

Effectively adds :kbd:`j` :kbd:`k` as a way to switch from
insert mode to normal mode, or as :mod:`prompt_toolkit` calls it, "navigation mode".

Also displays how to integrate :mod:`prompt_toolkit` and :mod:`IPython` together well.

:URL: https://ipython.readthedocs.io/en/stable/config/details.html#keyboard-shortcuts

.. todo:: Add one in for <C-M-j> to go to Emacs mode?

Example Usage
--------------
From the `source code`_::

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
from os.path import join

from IPython import get_ipython
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.vi_state import InputMode

logging.getLogger(name=__name__)


def _setup_logging(level, shell=None):
    logger = logging.getLogger(name=__name__)
    logger.setLevel(level)

    logdir = shell.profile_dir.log_dir
    log_file = join(logdir, 'keybinding.log')
    hdlr = logging.FileHandler(log_file)
    logger.addHandler(hdlr)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    return logger


def switch_to_navigation_mode(event):
    """Switches :mod:`IPython` from Vim insert mode to Vim normal mode.

    The function we can work with in the future if we want to change the
    keybinding for insert to navigation mode.
    """
    vi_state = event.cli.vi_state
    vi_state.input_mode = InputMode.NAVIGATION


def check_defaults():
    """What are the default keybindings we have here?

    Err I suppose I should say what does Prompt Toolkit export by default
    because I'm not 100% sure that ip imports everything or doesn't modify
    anything along the way.

    Probably gonna need to noqa something since the code isn't accessed as is.
    """
    registry = load_key_bindings()
    return registry.key_bindings


if __name__ == "__main__":
    _ip = get_ipython()

    level = logging.WARNING
    # logger = _setup_logging(level, shell=_ip)

    if getattr(_ip, 'pt_app', None):
        registry = _ip.pt_app.key_bindings
        registry.add_binding(
            u'j', u'k', filter=(HasFocus(DEFAULT_BUFFER)
                                & ViInsertMode()))(switch_to_navigation_mode)
