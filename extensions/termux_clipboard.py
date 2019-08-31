#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implement the paste magic on Termux.

IPython will simply fail as tkinter can't be installed.



See Also
--------
:mod:`IPython.lib.clipboard`
:mod:`IPython.core.hooks`

"""
import shutil
import subprocess

import IPython
from IPython.core.hooks import clipboard_get
from IPython.core.magic import line_magic


def termux_clipboard_get(self):
    p = subprocess.run(['termux-clipboard-get'], stdout=subprocess.PIPE)
    text = p.stdout
    from IPython.utils.py3compat import cast_unicode, DEFAULT_ENCODING
    unicode_text = cast_unicode(text, DEFAULT_ENCODING)
    return unicode_text


if __name__ == '__main__':
    from IPython import get_ipython
    shell = get_ipython()

    if shutil.which('termux-clipboard-get'):
        shell.set_hook(termux_clipboard_get)
