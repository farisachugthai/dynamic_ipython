#!/usr/bin/env python3
"""Rewrite how IPython implements pagers on Windows.

So would it be easier to do this as a magic or using Traitlets?

"""
import sys

from pygments.lexers.python import PythonLexer

from IPython import get_ipython
# Might need some of the funcs from IPython.utils.{PyColorize,coloransi,colorable}
from IPython.core.error import UsageError
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)


def lpad_ipython_docstring(shell):
    """TODO: Docstring for lpad_ipython_docstring.

    Parameters
    ----------
    shell : |ip|
        Global IPython object.

    Returns
    -------
    TODO

    """
    shell.register_magics(MyMagics)


@magic_arguments
def main():
    """Rewrite the module that creates the ``%pycat`` magic.

    In it's current implementation, the pager gives Windows a dumb terminal and
    never checks for whether :command:`less` is on the :envvar:`PATH` or
    if the user has a pager they wanna implement!

    :returns: TODO

    """
    pass


if __name__ == "__main__":
    _ip = get_ipython()
    main()
