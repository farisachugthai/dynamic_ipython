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
    r"""Custom exception hook for IPython.

    From the IPython official documentation:

        Print out a formatted exception traceback.
        Optional arguments:
          - out: an open file-like object to direct output to.

          - tb_offset: the number of frames to skip over in the stack, on a
            per-call basis (this overrides temporarily the instance's tb_offset
            given at initialization time.

    Parameters
    ----------
    ``*args``, ``**kwargs`` : list or dict
        The least useful call signature. Give it any length iterable.

    See Also
    --------
    :class:`IPython.core.ultratb.FormattedTB` : IPython.utils.colorable.Colorable
        Displays all accepted keyword arguments. Idk if I specified the type
        right but if you follow the MRU...

    Examples
    --------
    The following is the aforementioned FormattedTB class.::

        class FormattedTB(VerboseTB, ListTB):
            # Subclass ListTB but allow calling with a traceback.

            # It can thus be used as a sys.excepthook for Python > 2.1.

            # Also adds 'Context' and 'Verbose' modes, not available in ListTB.

            # Allows a tb_offset to be specified. This is useful for situations where
            # one needs to remove a number of topmost frames from the traceback (such as
            # occurs with python programs that themselves execute other python code,
            # like Python shells).

            def __init__(self, mode='Plain', color_scheme='Linux', call_pdb=False,
                         ostream=None,
                         tb_offset=0, long_header=False, include_vars=False,
                         check_cache=None, debugger_cls=None,
                         parent=None, config=None):

                # NEVER change the order of this list. Put new modes at the end:
                self.valid_modes = ['Plain', 'Context', 'Verbose', 'Minimal']
                self.verbose_modes = self.valid_modes[1:3]

                VerboseTB.__init__(self, color_scheme=color_scheme, call_pdb=call_pdb,
                                   ostream=ostream, tb_offset=tb_offset,
                                   long_header=long_header, include_vars=include_vars,
                                   check_cache=check_cache, debugger_cls=debugger_cls,
                                   parent=parent, config=config)

                # Different types of tracebacks are joined with different separators to
                # form a single string.  They are taken from this dict
                self._join_chars = dict(Plain='', Context='\n', Verbose='\n',
                                        Minimal='')
                # set_mode also sets the tb_join_char attribute
                self.set_mode(mode)

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
