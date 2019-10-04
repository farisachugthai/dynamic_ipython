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

from IPython import get_ipython, start_ipython


def main(shell=None):
    """Add all executables on the user's :envvar:`PATH` into the IPython ns.

    As this is the first script in startup, it's assumed IPython has already
    started. As a result, :func:`IPython.start_ipython` is called if not.

    Parameters
    ----------
    shell : |ip| instance
        IPython shell instance.

    """
    if shell is None:
        shell = start_ipython()
    shell.run_line_magic('rehashx', '')


if __name__ == "__main__":
    _ip = get_ipython()
    main(_ip)
