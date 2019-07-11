#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Show an example of how to create line and cell magics.

=============================================
Example of Writing A Custom IPython Extension
=============================================

.. module:: extensions.example
    :synopsis: Provide an example of creating IPython extensions.

---------------------------------------------

Writing Cell Magics
====================

While not utilized here, a similar execution path can be utilized for
:func:`IPython.core.magic.cell_magic()`

.. note::

    Don't use :func:`~IPython.core.magic.register_cell_magic()`.
    for this module. That decorator is for standalone functions that need to be
    registered as magics rather than classes.
    Conversely, :func:`~IPython.core.magic.register_magics()` is used for class
    based magics, and is more appropriate for this module.

See Also
========
:mod:`IPython.core.magic` : str
    Implementation of magics, magic_managers and instantiates objects to handle
    instances for interactive use. Useful reference for Jupyter notebooks as well.
:mod:`IPython.terminal.magic` : str
    Similar implementation specific to IPython.

"""
import sys
import time

from IPython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic


@magics_class
class ExampleMagic(Magics):

    def __init__(self, shell=None, **kwargs):
        super(ExampleMagic, self).__init__(shell)

    @line_magic
    def time_printer(self):
        """An example of a line magic."""
        if sys.platform.startswith('win'):
            return time.clock()
        else:
            return time.time()


def load_ipython_extension(shell=None):
    """Load the extension in IPython."""
    shell.register_magics(ExampleMagic)
    # _ip.register_magics(ExampleMagic.time_printer)
    shell.register_magic_function(ExampleMagic.time_printer)


if __name__ == "__main__":
    _ip = get_ipython()
    load_ipython_extension(_ip)
