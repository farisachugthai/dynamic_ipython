#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""Import my most frequently used modules.

==============
04_easy_import
==============

.. module:: 04_easy_import
    :synopsis: Import frequently used modules in the user namespace.

This imports a few utility functions from :ref:`IPython` and imports the python
package neovim is served in.


"""
import sys
from importlib import import_module

import IPython
from IPython.lib.deepreload import reload as __reload
from IPython.utils import importstring


def dreload(
        mod,
        extra_excludes=None,
        excludes=(
            'sys', 'os.path', 'builtins', '__main__', 'io', 'numpy',
            'numpy._globals', 'IPython'
        )
):
    """Import IPython's deepreload magic and modify the :param:`excludes` set.

    Parameters
    ----------
    mod : mod
        Module to reload
    extra_excludes : set of str, optional
        Extra modules to exclude from deepreload.
    excludes : set of str, optional
        Modules that won't be reloaded in order to preserve display and excepthooks.

    """
    if extra_excludes is not None:
        return __reload(mod, excludes=excludes + set(extra_excludes))
    else:
        return __reload(mod, excludes)


def import_nvim(mod):
    """Import the neovim module.

    Utilizes :func:`importlib.import_module()` from :mod:`importlib`.
    Nothing about the function is specific to nvim though, and it could be
    used for the entire package.

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
    if sys.version_info > (3, 5):  # actually shouldn't happen IPy requires 3.5>
        mod = 'pynvim'
    else:
        mod = 'neovim'

    import_nvim(mod)

    del import_nvim, mod
