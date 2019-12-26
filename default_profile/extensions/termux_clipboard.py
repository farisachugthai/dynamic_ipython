#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implement the `%paste` magic on Termux.

.. magic:: termux_clipboard_get

IPython will simply fail as tkinter can't be installed.

See Also
--------
:mod:`IPython.lib.clipboard`
:mod:`IPython.core.hooks`

"""
import shutil
import subprocess
import sys

# from prompt_toolkit.contrib
from IPython.core.getipython import get_ipython
from IPython.core.magic import line_magic, Magics, magics_class


@magics_class
class ClipboardMagics(Magics):
    """Haven't seen it implemented in a different way than this."""

    def __init__(self, shell=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shell = shell or get_ipython()

    def load_ipython_extension(self):
        """Sep 20, 2019: Works!"""
        self.shell.set_hook("clipboard_get", termux_clipboard_get)

    @line_magic
    def termux_clipboard_get(self):
        if not shutil.which("termux-clipboard-get"):
            return
        p = subprocess.run(["termux-clipboard-get"], stdout=subprocess.PIPE)
        text = p.stdout
        return text


@line_magic
def termux_clipboard_get(self):
    """Set the clipboard on termux using *termux_clipboard_get*.

    Whats the functional difference between declaring a line magic from
    a function or a method of a class?
    """
    if not shutil.which("termux-clipboard-get"):
        return
    p = subprocess.run(["termux-clipboard-get"], stdout=subprocess.PIPE)
    text = p.stdout
    return text
