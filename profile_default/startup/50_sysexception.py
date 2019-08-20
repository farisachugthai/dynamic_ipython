#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Give a detailed, colored traceback and drop into pdb on exceptions.

.. module:: 50_sysexception
   :synopsis: Specify a handler for IPython's traceback formatting.

"""
import sys

from IPython import get_ipython
from IPython.core import ultratb


class ExceptionHook(BaseException):
    """Custom exception hook for IPython.

    From the IPython official documentation:

    Print out a formatted exception traceback.

        Optional arguments:
          - out: an open file-like object to direct output to.

          - tb_offset: the number of frames to skip over in the stack, on a
            per-call basis (this overrides temporarily the instance's tb_offset
            given at initialization time.

    Parameters
    ----------
    *args, **kwargs : The least useful call signature

    See Also
    --------
    IPython.core.ultratb.FormattedTB
        Displays all accepted keyword arguments.

    """

    instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = ultratb.AutoFormattedTB(mode='Context',
                                                    color_scheme='Linux',
                                                    call_pdb=True,
                                                    ostream=sys.stdout)
        return self.instance(*args, **kwargs)

    def __repr__(self):
        """Don't actually know if it works this way."""
        return "<{} '{}'>".format(self.__class__.__name__, self.instance)


sys.excepthook = ExceptionHook()

if __name__ == '__main__':
    _ip = get_ipython()
    # So the InteractiveShell class tmk has an attribute called excepthook but
    # it's probably a bad idea to overwrite it
