#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Show an example of how to create line and cell magics.

Usage
-----
.. ipython::

    In [40]: %load_ext example


While not utilized here, a similar execution path can be utilized for
:func:`IPython.core.magic.cell_magic()`

05/22/2019

Functional again. Simple debugging because the stack traces are so easy to read.

See Also
--------
Utilize jedi and run ``:Pyimport IPython.core.magic`` to see the src.

.. note::

    Don't use register_cell_magic. That decorator is for functions.


"""
import sys
import time

from IPython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic


# register_cell_magic is only for functions
# from IPython.core.magic import register_cell_magic
# _ip.register_magics is only for classes lol oh my god
# from IPython.core.magic import register_magic


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
