#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""Import my most frequently used modules.

It seems that :mod:`IPython` and :mod:`traitlets` share a module!

From a cursory glance :mod:`traitlets.utils.importstring` ==
:mod:`IPython.utils.importstring`.

They both export 1 function :func:`~IPython.utils.importstring.import_item()`

This could be used here to dynamicallt import strings based on user
configuration, environment variables and configuration files.

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

    Utilizes :func:`import_module` from :mod:`importlib`.

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
    del import_nvim
