#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up pdb or ipdb.

.. code-block:: console

    $: ipdb3 -h

.. code-block:: none

    usage: python -m ipdb [-c command] ... pyfile [arg] ...
    Debug the Python program given by pyfile.
    Initial commands are read from .pdbrc files in your home directory
    and in the current directory, if they exist.  Commands supplied with
    -c are executed after commands from .pdbrc files.
    To let the script run until an exception occurs, use "-c continue".
    To let the script run up to a given line X in the debugged file, use
    "-c 'until X'"
    ipdb version 0.10.3.

Make `pp` use IPython's pretty printer, instead of the standard `pprint` module.

:URL: https://nedbatchelder.com/blog/200704/my_pdbrc.html

Jesus Christ this got out of control.

"""
print(".pdbrc.py started")

import atexit
import bdb
import cmd
from contextlib import suppress
import faulthandler
import importlib
import inspect
import os
from pathlib import Path
import pdb
from pprint import pprint
import runpy
import reprlib
import sys
import trace
import traceback

faulthandler.enable()

# I have a really useful module for importing readline on windows, linux,
# WSL, and anything else you can imagine. let's use it.
try:
    from default_profile.startup import readline_mod
except:   # noqa
    print('You did not import your readline mods in pdbrc.py')
else:
    readline_mod = runpy.run_path(Path('../startup/30_readline.py'), init_globals=globals())
    # runpy.run_path returns a dict with the modules namespace so let's get
    # the keys and check if we imported readline
    if 'readline' in readline_mod.keys():
        readline = readline_mod['readline']
    if 'setup_readline' in readline_mod.keys():
        setup_readline = readline_mod['setup_readline']
        setup_readline()

# Use IPython's pretty printing within PDB
with suppress(ImportError):
    from IPython.lib.pretty import pprint


# History

histfile = os.path.expanduser('~/.pdb_history')
try:
    readline.read_history_file(histfile)
except OSError:
    pass
else:
    readline.set_history_length(200)

atexit.register(readline.write_history_file, histfile)

# Customized Pdb


class MyPdb(pdb.Pdb):
    """Subclass pdb.Pdb."""

    def __init__(self, skip='traitlets', prompt=None, doc_header=None, *args, **kwargs):
        super().__init__(skip='traitlets', *args, **kwargs)
        self.prompt = prompt or 'YourPdb: '
        self.doc_header = doc_header or ''


# Customize the sys.excepthook


def exception_hook(type=None, value=None, tb=None):
    """Return to debugger after fatal exception (Python cookbook 14.5)."""
    if type or value or tb is None:
        type, value, tb = sys.exc_info()
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    traceback.print_exception(type, value, tb)
    pdb.pm()

sys.excepthook = exception_hook

print(".pdbrc.py finished")

# Vim: set ft=python:
