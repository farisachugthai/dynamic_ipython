#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""Import my most frequently used modules.

This imports a few utility functions from :ref:`IPython` and imports the python
package neovim is served in.

It seems that :mod:`IPython` and :mod:`traitlets` share a module!

From a cursory glance :mod:`traitlets.utils.importstring` ==
:mod:`IPython.utils.importstring`.

They both export 1 function :func:`~IPython.utils.importstring.import_item()`

This could be used here to dynamicallu import strings based on user
configuration, environment variables and configuration files.

The functionality here is duplicated in
:mod:`profile_default.extensions.easy_import`.


The Importance of Clean Namespaces
==================================
May 07, 2019:

    If the last line in the module didn't have ``del mod`` in it, then
    the magic ``%pylab`` would crash!

    It uses the same keyword behind the scenes interestingly enough.

.. todo:: Could add in :func:`wcwidth.wcswidth()` to determine width of output
          device and print that many ``***`` for the nvim part.

"""
from importlib import import_module
import os
from pathlib import Path
import shutil
from shutil import which, chown, copytree  # noqa: E401
import subprocess
import sys

from IPython.utils.dir2 import dir2, get_real_method, safe_hasattr
from IPython.core.interactiveshell import InteractiveShell

# 12/14/18
import IPython

try:
    import git
except ImportError:
    pass


def import_nvim(mod):
    """Import the neovim module.

    Utilizes :func:`import_module` from :mod:`importlib`. Nothing about the
    function is specific to nvim though, and it could be used for the entire
    module.

    :param mod: A module to import.
    :returns: None
    """
    try:
        import_module(mod)
    except ImportError:
        print("************************************************************")
        print("{} import failed. Only ignore this if you plan on going"
              " the entire session without using %edit".format(mod))
        print("************************************************************")


if __name__ == "__main__":
    if sys.version_info > (3, 5):
        mod = 'pynvim'
    else:
        mod = 'neovim'

    import_nvim(mod)

    del import_nvim, mod
