#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Give a detailed, colored traceback and drop into pdb on exceptions.

This may have proved obvious to some but don't call
get_ipython().atexit_operations() during a terminal session you intend
on continuing....

So the IPython.core.ultratb mod was stated to be a port of cgitb.

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

    def __init__(self, shell=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shell = shell

    def call(self, etype=None, evalue=None, etb=None):
        """Proxy for the call dunder."""
        if etype is None and evalue is None and etb is None:
            etype, evalue, etb = sys.exc_info()
        self.__call__(self, etype, evalue, etb)

    def __call__(self, etype, evalue, etb):
        """TODO."""
        pass

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
