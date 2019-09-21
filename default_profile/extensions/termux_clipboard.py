#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implement the `%paste` magic on Termux.

.. module:: termux_clipboard_get
    :synopsis: Set up termux for the paste magic.

IPython will simply fail as tkinter can't be installed.

See Also
--------
:mod:`IPython.lib.clipboard`
:mod:`IPython.core.hooks`

"""
import shutil
import subprocess
import sys

from IPython.core.magic import line_magic


@line_magic
def termux_clipboard_get(self):
    """Set the clipboard on termux using *termux_clipboard_get*."""
    p = subprocess.run(['termux-clipboard-get'], stdout=subprocess.PIPE)
    text = p.stdout
    from IPython.utils.py3compat import cast_unicode, DEFAULT_ENCODING
    unicode_text = cast_unicode(text, DEFAULT_ENCODING)
    return unicode_text


def load_ipython_extension(ip):
    """Sep 20, 2019: Works!"""
    ip.set_hook('clipboard_get', termux_clipboard_get)


def main():
    """Main function.

    Returns
    -------
    TODO

    """
    from IPython import get_ipython
    shell = get_ipython()

    if not shell:
        return

    if shutil.which('termux-clipboard-get'):
        # shell.set_hook(termux_clipboard_get)
        load_ipython_extension(shell)


if __name__ == '__main__':
    sys.exit(main())
