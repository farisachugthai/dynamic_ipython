#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Magic that reads in a string and parses it as a :mod:`CSV` with :mod:`pandas`.

Example of creating a magic from **IPython Interactive Computing and
Visualization Cookbook by Cyrille Roussou.**

The example specifically is from pages 32 to 35.

It also shows the following simpler example:

.. ipython::

    In [1]: from IPython.core.magic import (register_line_magic, register_cell_magic)
    In [2]: @register_line_magic
            def hello(line):
                if line == 'french':
                    print("Salut tout le monde!")
                else:
                    print("Hello world!")

"""
import sys
from io import StringIO

try:
    import pandas as pd
except ImportError:
    sys.exit("Pandas not installed. Exiting.")


def csv(cell):
    """Read in an :class:`io.StringIO()` and parse it with the pandas library."""
    sio = StringIO(cell)
    return pd.read_csv(sio)


def load_ipython_extension(ip):
    """This function is called when the extension is loaded.

    It accepts an IPython |ip| instance. We can register the magic with the
    `register_magic_function` method.
    """
    ip.register_magic_function(csv, 'cell')
