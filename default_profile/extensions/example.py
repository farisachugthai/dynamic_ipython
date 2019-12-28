#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================
Example of Writing A Custom IPython Extension
=============================================

Usage
-----

.. ipython::

    In [40]: %load_ext example


Writing Cell Magics
--------------------

While not utilized here, a similar execution path can be utilized for
:func:`IPython.core.magic.cell_magic()`


Those lines specifically.

See Also
--------
IPython.core.magic
IPython.terminal.magic

"""
import sys
import time

from IPython import get_ipython
from IPython.core.magic import Magics, line_magic, magics_class


@magics_class
class ExampleMagic(Magics):
    def __init__(self, shell=None, **kwargs):
        super(ExampleMagic, self).__init__(shell)

    @line_magic
    def time_printer(self):
        """An example of a line magic."""
        if sys.platform.startswith("win"):
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
