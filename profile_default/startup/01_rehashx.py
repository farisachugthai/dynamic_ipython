#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rehash immediately to add everything in :envvar:`$PATH` as a line alias.

=======
Rehash
=======

.. module:: 01_rehashx

This is an incredible little gem I just ran into, and hugely useful for
making IPython work as a more versatile system shell.

Help
-----

Help on :func:`~IPython.core.interactiveshell.run_line_magic()`.

.. code-block:: none

    run_line_magic(magic_name, line, _stack_depth=1)
    method of |ip| instance
    Execute the given line magic.


Parameters
----------
magic_name : str
    Name of the desired magic function, without '%' prefix.
line : str
    The rest of the input line as a single string.
_stack_depth : int
    If :func:`IPython.core.magics.run_line_magic()` is called from
    :func:`IPython.core.magics.magic()` then
    `_stack_depth` = 2. This is added to ensure backward compatibility for use
    of :func:`IPython.core.magics.get_ipython().magic()`


Usage
------

As the help outlines above, the second required positional argument to
:func:`IPython.core.TerminalInteractiveShell.run_line_magic()` is `line`.

This is more easily understood as 'remaining arguments to the magic'.
``%rehashx`` takes none, but leaving it blank causes the function call to raise
an error, so an empty str is passed to the function.


"""
import logging
import sys

from IPython import get_ipython
from IPython.core.alias import AliasError

from profile_default.util.timer import timer


def blacklisted_aliases(shell=None):
    """Remove aliases that would otherwise raise errors."""
    blacklist = ['more', 'less', 'clear', 'man']
    for i in blacklist:
        try:
            shell.run_line_magic('alias', '-d {}'.format(i))
        except AliasError:
            pass


@timer
def main(shell=None):
    """Check if :mod:`IPython` was initialized and if so, ``%rehashx``."""
    shell.run_line_magic('rehashx', '')

    blacklisted_aliases(shell)

    return shell


if __name__ == "__main__":
    LOGGER = logging.getLogger(name=__name__)
    LOG_LEVEL = logging.INFO
    LOGGER.setLevel(LOG_LEVEL)

    _ip = get_ipython()

    _ip = main(_ip)
