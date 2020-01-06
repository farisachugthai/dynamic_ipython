#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up pdb with readline, history management, and fault handling.

Make `pp` use IPython's pretty printer, instead of the standard `pprint` module.

:URL: https://nedbatchelder.com/blog/200704/my_pdbrc.html

Jesus Christ this got out of control.

"""
from contextlib import suppress
import faulthandler
import os
from pathlib import Path
import pdb
from pprint import pprint
import runpy
import sys
import trace

pprint(".pdbrc.py started")

faulthandler.enable()


# Use IPython's pretty printing within PDB
with suppress(ImportError):
    from IPython.lib.pretty import pprint


# I have a really useful module for importing readline on windows, linux,
# WSL, and anything else you can imagine. let's use it.
try:
    from default_profile.startup import __main__
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


# History: Set up separately
try:
    from default_profile.startup.readline_mod import set_historyfile
except:  # noqa
    pass
else:
    set_historyfile("~/.pdb_history")


# Customized Pdb


class MyPdb(pdb.Pdb):
    """Subclass pdb.Pdb."""

    def __init__(self, skip="traitlets", prompt=None, doc_header=None, *args, **kwargs):
        self.skip = skip
        self.prompt = prompt or "YourPdb: "
        self.doc_header = doc_header or ""
        super().__init__(
            skip=self.skip,
            prompt=self.prompt,
            doc_header=self.doc_header,
            *args,
            **kwargs
        )


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

print(".pdbrc.py finished")
