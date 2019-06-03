#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Show an example of how to create line and cell magics.

=============================================
Example of Writing A Custom IPython Extension
=============================================

Usage
=====

.. ipython::

    In [40]: %load_ext example


Writing Cell Magics
====================

While not utilized here, a similar execution path can be utilized for
:func:`IPython.core.magic.cell_magic()`

.. note::

    Don't use register_cell_magic. That decorator is for functions.
    `~IPython.core.magic.register_magics` is only for classes as well.

::

    from IPython.core.magic import register_cell_magic
    from IPython.core.magic import register_magic

Those lines specifically.

See Also
========
IPython.core.magic
IPython.terminal.magic

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
    _ip.register_magics(ExampleMagic)
    # _ip.register_magics(ExampleMagic.time_printer)
    _ip.register_magic_function(ExampleMagic.time_printer)


if __name__ == "__main__":
    _ip = get_ipython()
    load_ipython_extension(_ip)
