#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rehash immediately to add everything in :envvar:`$PATH` as a line alias.

Rehash
=======

This is an incredible little gem I just ran into, and hugely useful for
making IPython work as a more versatile system shell.

Help
-----
Help on :func:`~IPython.core.interactiveshell.run_line_magic()`::

    run_line_magic(magic_name, line, _stack_depth=1)
    method of IPython.terminal.interactiveshell.TerminalInteractiveShell instance
    Execute the given line magic.


Parameters
----------
magic_name : str
    Name of the desired magic function, without '%' prefix.

line : str
    The rest of the input line as a single string.

_stack_depth : int
    If :func:`IPython.core.magics.run_line_magic()` is called from :func:`IPython.core.magics.magic()` then
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
import platform
import sys

from IPython import Application, get_ipython


def _sys_check():
    """Check OS."""
    return platform.uname().system


def main():
    """Check if we're on Windows and if not rehashx.

    05/06/2019:

        ``%rehashx`` when run in a directory with symlinks while on Windows 10
        causes an unexpected error. Quite specific but hey.

    """
    if not Application.initialized():
        sys.exit()

    if not _sys_check() == 'Windows':
        _ip = get_ipython()
        _ip.run_line_magic('rehashx', '')


if __name__ == "__main__":
    main()
