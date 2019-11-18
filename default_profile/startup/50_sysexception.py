#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Give a detailed, colored traceback and drop into pdb on exceptions.

This may have proved obvious to some but don't call
get_ipython().atexit_operations() during a terminal session you intend
on continuing....

"""
import sys
from abc import ABC
from collections.abc import Sequence

from IPython import get_ipython
from IPython.core import ultratb

from traitlets.config import Configurable


class ExceptionHook(Configurable):
    """Custom exception hook for IPython."""

    instance = None

    def call(self, *args, **kwargs):
        """Proxy for the call dunder."""
        self.__call__(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = ultratb.AutoFormattedTB(
                mode="Context", color_scheme="Linux", call_pdb=True, ostream=sys.stdout
            )
        return self.instance(*args, **kwargs)

    def __repr__(self):
        """Don't actually know if it works this way."""
        return "<{} '{}'>".format(self.__class__.__name__, self.instance)


class ExceptionTuple(Sequence, ABC):
    """Simply a test for now but we need to provide the exception hook with this.

    It needs a tuple of exceptions to catch.

    Seemed like a good place to keep working with ABCs.
    """

    # raise NotImplementedError
    pass


if __name__ == "__main__":
    # _ip = get_ipython()
    # So the InteractiveShell class tmk has an attribute called excepthook but
    # it's probably a bad idea to overwrite it
    # sys.excepthook = ExceptionHook()

    # _ip.set_custom_exc(ExceptionHook())
    pass
