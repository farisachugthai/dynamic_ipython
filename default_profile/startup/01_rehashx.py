#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========
`%rehashx`
==========

This is an incredible little gem that's hugely useful for
making IPython work as a more versatile system shell.

For the future we should consider moving all imports from this package out and
keeping only "*Mission Critical*" type code in the first file.

The code that's more important than anything should execute regardless
of whether someone has ``pip install``-ed it.

"""
import logging
from platform import system
import sys

from IPython import get_ipython
from IPython.core.alias import AliasError

try:
    from default_profile.util.timer import timer
except Exception:
    timer = None
    # is this a way to "None" a decorator? Nope!


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


def main(shell=None):
    """Add all executables on the user's :envvar:`PATH` into the IPython ns."""
    shell.run_line_magic('rehashx', '')


if __name__ == "__main__":
    _ip = get_ipython()
    if _ip:
        main(_ip)
