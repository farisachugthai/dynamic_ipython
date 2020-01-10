#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up pdb with readline, history management, and fault handling.

Make `pp` use IPython's pretty printer, instead of the standard `pprint` module.

:URL: https://nedbatchelder.com/blog/200704/my_pdbrc.html

Jesus Christ this got out of control.

"""
import atexit
from contextlib import suppress
import faulthandler
import logging
import os
from pathlib import Path
import pdb
import runpy
import sys
import time
import trace

# Run all this before any non-std lib imports. They should get profiled too
print(f".pdbrc.py started {time.ctime()}")

start = time.time()
logger = logging.getLogger(name=__name__)
faulthandler.enable()

try:
    from prompt_toolkit.shortcuts import print_formatted_text as print
except:  # noqa
    from pprint import pprint as print
try:
    from IPython.core.getipython import get_ipython
except:  # noqa
    shell = None
else:
    shell = get_ipython()


# Use IPython's pretty printing within PDB
with suppress(ImportError):
    from IPython.lib.pretty import pprint


# I have a really useful module for importing readline on windows, linux,
# WSL, and anything else you can imagine. let's use it.
try:
    from default_profile.startup import __main__
except:  # noqa
    try:
        import readline
    except:  # noqa
        print("You did not import your readline mods in pdbrc.py")
else:

    readline_mod = runpy.run_path(
        Path("../startup/30_readline.py").__fspath__(), init_globals=globals()
    )
    # runpy.run_path returns a dict with the modules namespace so let's get
    # the keys and check if we imported readline
    if "readline" in readline_mod.keys():
        readline = readline_mod["readline"]
    if "setup_readline" in readline_mod.keys():
        setup_readline = readline_mod["setup_readline"]
        setup_readline()


def save_history(hist_path=None):
    if not readline:
        return
    if not hasattr(readline, "append_history_file"):
        print("ERR: no append_history_file method in readline")
        return
    if not hist_path:
        hist_path = Path("~/.pdb_history.py").resolve()
        if not hist_path.exists():
            logging.warning("Creating PDB history file at ~/.pdb_history.")
            hist_path.touch()

    readline.append_history_file(hist_path)


# History: Set up separately
try:
    from default_profile.startup import readline_mod
except:  # noqa
    historyPath = Path.expanduser("~/.pdb_history.py")

    if historyPath.exists():
        readline.read_history_file(historyPath)
        save_history(historyPath)

    atexit.register(save_history, hist_path=historyPath)
else:

    readline_mod.setup_historyfile("~/.pdb_history")


# Customized Pdb


class MyPdb(pdb.Pdb):
    """Subclass pdb.Pdb. Goddamn the only kw it uses that I wrote was skip."""

    prompt = f"<YourPdb> : "
    doc_header = ""

    def __init__(self, skip="traitlets", prompt=None, doc_header=None, shell=None, *args, **kwargs):
        self.skip = skip
        self.prompt = prompt
        self.doc_header = doc_header
        self.shell = shell
        if self.shell is not None:
            self.prompt += " [" + self.shell.execution_count + "]: "
        super().__init__(skip=self.skip, *args, **kwargs)

    def __repr__(self):
        return repr(self.__class__.__name__)

    def run(self):
        # This is the important one
        super().run()


debugger = MyPdb()
# TODO:
# get_ipython().debugger_cls = MyPdb

# Customize the sys.excepthook

def exception_hook(type=None, value=None, tb=None):
    """Return to debugger after fatal exception (Python cookbook 14.5)."""
    if type or value or tb is None:
        type, value, tb = sys.exc_info()
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    traceback.print_exception(type, value, tb)
    pdb.pm()


sys.excepthook = exception_hook

end = time.time()
duration = end - start
print(".pdbrc.py finished.{time.ctime()}\nduration was: {duration}.\n")
