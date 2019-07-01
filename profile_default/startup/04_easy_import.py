#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""Import my most frequently used modules.

==============
04_easy_import
==============

.. currentmodule:: 04_easy_import

This imports a few utility functions from :ref:`IPython` and imports the python
package neovim is served in.

Overlap between IPython and traitlets
======================================

It seems that :mod:`IPython` and :mod:`traitlets` share a module!

From a cursory glance :mod:`traitlets.utils.importstring` ==
:mod:`IPython.utils.importstring`.

They both export 1 function: :func:`~IPython.utils.importstring.import_item()`

This could be used here to dynamicallu import strings based on user
configuration, environment variables and configuration files.

.. warning: Pending Deprecation: The functionality here is duplicated in
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
import sys
from importlib import import_module

# don't do this anymore because it'll mess up the line alias:: alias %git git %l
# try:
#     from git import Git
# except (ImportError, ModuleNotFoundError):
#     pass


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
    None

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
