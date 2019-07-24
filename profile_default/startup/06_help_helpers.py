#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export functions to redirect :func:`help` output.

============
Help Helpers
============

.. currentmodule:: 06_help_helpers
    :synopsis: Export functions that aide working with the :func:`help` builtin.

This module utilizes the examples given in the official documentation
for :mod:`contextlib`!

In addition to utilizing contextlib, create a function that allows
for an easier "grep-like" utility through objects that are too large
to simply skim the output of :func:`dir()`.

------------------

.. todo:: :mod:`pydoc` actually has a giant API so we could also use that.


"""
import contextlib
import re
import sys

from IPython import get_ipython

_ip = get_ipython()


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
    """WIP."""
    _ip.pinfo(arg)


def grep(obj, pattern=['^a-z.*$']):
    compiled = re.compile(pattern)
    attributes = dir(obj)
    print('\n'.join(i for i in attributes if re.search(compiled, i)))
