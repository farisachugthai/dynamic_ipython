#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set printing options.

"""
import ctypes
import doctest
import logging
import platform
import sys

logging.basicConfig(
    level=logging.WARNING, stream=sys.stdout, format=logging.BASIC_FORMAT
)


if platform.system() == "Windows":
    from ctypes import WinDLL


def numpy_setup():
    """Jeez this got platform specific."""
    try:
        import numpy as np
    except (ImportError, ModuleNotFoundError):
        set_numpy_printoptions = None
    except OSError as e:

        ###########
        # WAIT WHAT
        ###########

        # If you catch an exception like this, does it not appear in sys.exc_info()
        # anymore or am i being an idiot?
        # Check again in the morning

        if getattr(sys, "last_type", None):
            if sys.last_type == "WindowsError":
                sys.exit("Goddamnit Numpy. ctypes is fucking up again.")
            else:
                logging.exception(e)
                return
        else:
            return
    else:
        return True  # i guess just return true to indicate success?


def set_numpy_printoptions(**kwargs):
    """Define this function only if numpy can be imported.

    But don't end the script with sys.exit() because anything that imports
    this module will exit too. As the ``__init__.py`` imports this module
    the whole package breaks due to a simple installation issue.

    Parameters
    ----------
    kwargs : dict
        Any options that should be overridden.

    """
    np.set_printoptions(threshold=20)
    if kwargs is not None:
        np.set_printoptions(**kwargs)


if __name__ == "__main__":
    numpy_mod = numpy_setup()
    if numpy_mod is True:
        import numpy as np

        # setup worked so import it as normal
        set_numpy_printoptions()
