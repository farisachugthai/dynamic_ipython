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

from IPython.core.getipython import get_ipython
from IPython.core.magic import line_magic, Magics, magics_class


@magics_class
class ClipboardMagics(Magics):
    """Haven't seen it implemented in a different way than this."""

    def __init__(self, shell=None, *args, **kwargs):
        """Bind the IPython instance and it's config and parent attributes."""
        self.shell = shell or get_ipython()
        if self.shell is not None:
            if getattr(self.shell, "config", None):
                self.config = self.shell.config
            else:
                self.config = None

            if getattr(self.shell, "parent", None):
                self.parent = self.shell.parent
            else:
                self.parent = None

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "<{}>:".format(self.__class__.__name__)

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
    def pyperclip_magic(self):
        try:
            # This is what you were looking for.
            from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
        except ModuleNotFoundError:
            # womp
            print("pyperclip not imported.")
        else:
            self.shell.pt_app.clipboard = PyperclipClipboard()
