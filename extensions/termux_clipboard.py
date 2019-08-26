#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implement the paste magic on Termux.

IPython will simply fail as tkinter can't be installed.

Just scraped this together using the osx function.::

    In [117]: def termux_clipboard_get():
         ...:     p = subprocess.run(['termux-clipboard-get'], stdout=subprocess.PIPE)
         ...:     text = p.stdout
         ...:     from IPython.utils.py3compat import cast_unicode, DEFAULT_ENCODING
         ...:     unicode_text = cast_unicode(text, DEFAULT_ENCODING)
         ...:     return unicode_text

See Also
--------
:mod:`IPython.lib.clipboard`
:mod:`IPython.core.hooks`

"""
import subprocess

import IPython
from IPython.core.hooks import clipboard_get
from IPython.core.magic import line_magic
