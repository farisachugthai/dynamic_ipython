#!/usr/bin/env python
"""
========================================================================
`%load_ext` --- Import commonly used modules into the IPython namespace.
========================================================================

.. magic:: load_ext

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
        raise UsageError("Missing module name.")
    else:
        res = shell.extension_manager.load_extension(module_str)
        if res == "already loaded":
            logging.warning(
                "The %s extension is already loaded. To reload it, use:" % module_str
            )
            print("%reload_ext", module_str)

        elif res == "no load function":
            logging.error("The %s module is not an IPython extension." % module_str)


if __name__ == "__main__":
    _ip = get_ipython()
    if _ip is None:
        sys.exit()

    args = sys.argv[1:]

    if len(args) == 0:
        load_ipython_extension(_ip)
    elif len(args) > 0:
        for i in args:
            load_ext(i, shell=_ip)
    else:
        raise IndexError
