#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rehash
=======

This is an incredible little gem I just ran into, and hugely useful for
making `IPython` work as a more versatile system shell.


Parameters
----------
magic_name : str
    Name of the desired magic function, without :kbd:`%` prefix.
line : str
    The rest of the input line as a single string.
``_stack_depth`` : int, optional
    Number of recursive calls to an IPython magic.


Notes
-----
IPython.core.magic.run_line_magic
    A method of the |ip| instance to run a specific magic currently in the
    IPython.core.interactiveshell.InteractiveShell.user_ns
    or user namespace.


.. ipython::
    :verbatim:

    from IPython.core import get_ipython
    shell = get_ipython()
    shell.run_line_magic('ls', '')


Usage
------
As the help outlines above, the second required positional argument to
:func:`IPython.core.TerminalInteractiveShell.run_line_magic` is ``line``.

This is more easily understood as 'remaining arguments to the magic'.
`%rehashx` takes none, but leaving it blank causes the function call to raise
an error, so an empty `str` is passed to the function.


``_stack_depth``
~~~~~~~~~~~~~~~~
The ``_stack_depth`` parameter can be understood like so:

If :func:`IPython.core.magics.run_line_magic` is called from
:func:`IPython.core.magics.magic` then
``_stack_depth`` = 2.

This is added to ensure backward compatibility for use
of :func:`IPython.core.magics.get_ipython().magic`

-----------------

"""
import logging
from platform import system
import sys

from IPython import get_ipython
from IPython.core.alias import AliasError

from default_profile.util.timer import timer


def blacklisted_aliases(shell=None):
    """Blacklist certain aliases.

    On Windows, it's assumed that the commands *more*, *less*, *clear* and
    *man* are undefined. However, the Git-For-Windows package provides all
    of these and by adding it to the :envvar:`PATH`, `rehashx` will attempt
    to alias them, resulting in a UsageError.

    Parameters
    ----------
    shell : |ip|, optional

    Raises
    ------
    AliasError

    """
    blacklist = ['more', 'less', 'clear', 'man']
    for i in blacklist:
        try:
            shell.run_line_magic('unalias', '{}'.format(i))
        except AliasError:
            pass


@timer
def main(shell=None):
    """Add all executables on the user's :envvar:`PATH` into the IPython ns."""
    shell.run_line_magic('rehashx', '')


if __name__ == "__main__":
    logging.BASIC_FORMAT = '%(created)f : %(levelname)s : %(module)s : %(message)s : '
    rehashx_logger = logging.getLogger('default_profile'
                                       ).getChild('startup.rehashx')

    rehashx_stream = logging.StreamHandler()
    rehashx_formatter = logging.Formatter(logging.BASIC_FORMAT)

    rehashx_stream.setFormatter(rehashx_formatter)
    rehashx_stream.setLevel(logging.WARNING)
    rehashx_logger.addHandler(rehashx_stream)
    rehashx_logger.setLevel(logging.WARNING)

    _ip = get_ipython()
    if _ip:
        main(_ip)
