#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
============
Help Helpers
============

Export functions to redirect :func:`help` output.

This module utilizes the examples given in the official documentation
for :mod:`contextlib`.

In addition to utilizing :mod:`contextlib`, we create a function that allows
that allows searching through the members of an object.

This is intended to be exposed to the user as a quick, interactive tool
with an easier "grep-like" interface for objects that are too large
to be quickly and easily understood based on the output of :func:`dir`.

.. todo:: :mod:`pydoc` actually has a giant API so we could also use that.


"""
import contextlib
import re
import sys


def print_help(arg=None):
    """Redirect :func:`help` to ``sys.stderr``."""
    with contextlib.redirect_stdout(sys.stderr):
        help(arg)


def save_help(arg=None, output_file=sys.stdout):
    """Write :func:`help` to a file. Defaults to ``sys.stdout``."""
    with open(output_file, 'xt') as f:
        with contextlib.redirect_stdout(f):
            help(arg)


def page_help(arg=None):
    """Using IPython's `pinfo` magic to page information to the console.

    Also noting it's the only function in this module that actually needs
    the IPython instance so the imports were moved here.
    """
    from IPython import get_ipython
    _ip = get_ipython()
    if hasattr(_ip, 'pinfo'):
        _ip.pinfo(arg)


def grep(obj, pattern=['^a-z.*$']):
    compiled = re.compile(pattern)
    attributes = dir(obj)
    print('\n'.join(i for i in attributes if re.search(compiled, i)))
