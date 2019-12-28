#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===========
Extensions
===========

This houses a collection of IPython extensions I've written.

Many are still works in progress.


"""
import logging

from . import cwd_prompt, example
from .event_watcher_example import VarWatcher
from .job_control import install
from .pd_csv import pd_csv
from .termux_clipboard import ClipboardMagics

extensions_logger = logging.getLogger(name="default_profile").getChild("extensions")
extensions_handler = logging.StreamHandler()
extensions_handler.setLevel(logging.WARNING)
extensions_handler.setFormatter(logging.Formatter())
extensions_logger.setLevel(logging.WARNING)
extensions_logger.addHandler(extensions_handler)

# currently has a syntax error so fix that before we continue importing
# from . import extension_inspect


def load_ipython_extension(shell=None):
    """Register load_ext as an extension.

    From :func:`IPython.core.magic.MagicsManager.register_function()`:

        This will create an IPython magic (line, cell or both) from a
        standalone function.  The functions should have the following
        signatures:

    * For line magics: ``def f(line)``
    * For cell magics: ``def f(line, cell)``
    * For a function that does both: ``def f(line, cell=None)``

    In the latter case, the function will be called with ``cell==None`` when
    invoked as ``%f``, and with cell as a string when invoked as ``%%f``.

    """
    shell.magics_manager.register_function(load_ext, magic_name="load_ext")
