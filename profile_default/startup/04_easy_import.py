#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""
==============
04_easy_import
==============

.. module:: 04_easy_import
    :synopsis: Import frequently used modules in the user namespace.

This imports a few utility functions from :mod:`IPython` and imports the python
package neovim is served in.


"""
import sys
from importlib import import_module

import IPython
from IPython.lib.deepreload import reload as _reload
from IPython.utils import importstring


class DeepReload:
    """Load IPython's `%deepreload` magic.

    Attributes
    ----------
    excludes : set of str, optional
        Modules that won't be reloaded in order to preserve display
        and excepthooks.

    """
    excludes = (
        'sys', 'os.path', 'builtins', '__main__', 'io', 'numpy',
        'numpy._globals', 'IPython'
    )

    def __init__(self, excludes=None):
        self.excludes = excludes

    def dreload(self, mod, extra_excludes=None):
        """Import IPython's `%deepreload` magic.

        This function exists to modify the ``excludes`` set.

        Parameters
        ----------
        mod : mod
            Module to reload
        extra_excludes : set of str, optional
            Extra modules to exclude from `IPython.lib.deepreload.dreload`.
        """
        if extra_excludes is not None:
            return _reload(mod, self.excludes + set(extra_excludes))
        else:
            return _reload(mod, self.excludes)


def easy_import(mod):
    """Import a module.

    Utilizes :func:`importlib.import_module()` from :mod:`importlib` so that
    any valid alphanumeric string can be passed without crashing the
    interpreter.

    Parameters
    ----------
    mod : str
       A module to import.

    Returns
    -------
    pynvim : mod
        Neovim's python module.

    """
    try:
        pynvim = import_module(mod)
    except ImportError:
        print("************************************************************")
        print(
            "{} import failed. Only ignore this if you plan on going"
            " the entire session without using %edit".format(mod)
        )
        print("************************************************************")
    else:
        return pynvim


if __name__ == "__main__":
    if sys.version_info > (3, 5):
        mod = 'pynvim'
    else:
        mod = 'neovim'

    easy_import(mod)
