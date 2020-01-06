#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the main startup for the IPython startup directory.

.. todo::

    So I think a good idea would be make this directory something that can be
    executed with 1 command, combine that and export it here.
    If something goes wrong in startup IPython doesn't finish executing the remaining files.
    So make it easy to re-exec.

"""
import sys

from IPython.core.getipython import get_ipython

# Are you allowed to do this? This shit confuses me so much
# Nope
# from . import STARTUP_LOGGER

shell = get_ipython()

if not shell:
    sys.exit("startup.__main__: get_ipython returned None")


def exec_startup():
    """Be careful!!

    .. danger::
        All of the usual exec admonitions apply here.

    """
    exec (compile(
        open(__file__).read(),
        '<string>',
        'exec',
    ), globals(), locals())
