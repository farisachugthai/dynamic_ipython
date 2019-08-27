#!/usr/bin/env python
"""
========================================================================
`%load_ext` --- Import commonly used modules into the IPython namespace.
========================================================================
.. magic:: load_ext

.. module:: load_ext
    :synopsis: Import commonly used modules into the IPython namespace.

This module is a slightly different way of accomplishing what
:mod:`profile_default.startup.04_easy_import` attempts to do.

Specifically, it sets up importing things into the user's interactive namespace.

"""
import logging
import sys

from IPython import get_ipython
from IPython.core.error import UsageError
from IPython.core.magic import line_magic

logging.basicConfig(level=logging.WARNING, format=logging.BASIC_FORMAT)


@line_magic
def load_ext(module_str, shell=None):
    """Load an IPython extension by its module name."""
    if not module_str:
        raise UsageError('Missing module name.')
    else:
        res = shell.extension_manager.load_extension(module_str)
        if res == 'already loaded':
            logging.warning(
                "The %s extension is already loaded. To reload it, use:" %
                module_str
            )
            print("%reload_ext", module_str)

        elif res == 'no load function':
            logging.error(
                "The %s module is not an IPython extension." % module_str
            )


def load_ipython_extension(shell=None):
    """Register load_ext as an extension.

    From :func:`IPython.core.magic.MagicsManager.register_function()`:

        This will create an IPython magic (line, cell or both) from a
        standalone function.  The functions should have the following
        signatures:

        * For line magics: `def f(line)`
        * For cell magics: `def f(line, cell)`
        * For a function that does both: `def f(line, cell=None)`

        In the latter case, the function will be called with ``cell==None`` when
        invoked as ``%f``, and with cell as a string when invoked as ``%%f``.

    """
    shell.magics_manager.register_function(load_ext, magic_name='load_ext')


if __name__ == "__main__":
    _ip = get_ipython()
    args = sys.argv[1:]
    if len(args) == 0:
        # TODO: Use magic_arguments decorator
        sys.exit('E127')
    elif len(args) > 0:
        for i in args:
            module_str = sys.argv[i]
            load_ext(module_str, shell=_ip)
    else:
        raise IndexError
