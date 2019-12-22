#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Give a detailed, colored traceback and drop into pdb on exceptions.

This may have proved obvious to some but don't call
get_ipython().atexit_operations() during a terminal session you intend
on continuing....

So the IPython.core.ultratb mod was stated to be a port of cgitb.

Let's check out the source for that then right?

class Hook:
    # A hook to replace sys.excepthook that shows tracebacks in HTML.
    def __init__(self, display=1, logdir=None, context=5, file=None,
                 format="html"):
        self.display = display          # send tracebacks to browser if true
        self.logdir = logdir            # log tracebacks to files if not None
        self.context = context          # number of source code lines per frame
        self.file = file or sys.stdout  # place to send the output
        self.format = format

Looks like we're in business!

"""
import sys
from collections.abc import Sequence
import cgitb

from IPython.core.getipython import get_ipython

from traitlets.config import Configurable


class ExceptionHook(Configurable):
    """Custom exception hook for IPython."""

    instance = None

    def call(self, *args, **kwargs):
        """Proxy for the call dunder."""
        self.__call__(self, *args, **kwargs)

    # def __call__(self, *args, **kwargs):
    #     if self.instance is None:
    #         self.instance = ultratb.AutoFormattedTB(
    #             mode="Context", color_scheme="Linux", call_pdb=True, ostream=sys.stdout
    #         )
    #     return self.instance(*args, **kwargs)

    def __repr__(self):
        """Don't actually know if it works this way."""
        return "<{} '{}'>".format(self.__class__.__name__, self.instance)


class ExceptionTuple(Sequence):
    """Simply a test for now but we need to provide the exception hook with this.

    It needs a tuple of exceptions to catch.

    Seemed like a good place to keep working with ABCs.
    """

    # raise NotImplementedError
    pass


if __name__ == "__main__":
    shell = get_ipython()
    handled = cgitb.Hook(logdir=shell.profile_dir.log_dir, file=sys.stdout, format='text')
    sys.excepthook = handled
