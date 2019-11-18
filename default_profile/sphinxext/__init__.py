#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================
IPython-specific Sphinx extensions.
===================================

Imports the modules found in the current directory and utilizes
:mod:`pkgutil` and :func:`pkgutil.extend_path`
to extend the packages ``__path__`` parameter.

It only imports the modules below if this repository has been installed.

If this weren't true, then starting IPython without this package installed
would emit :exc:`ImportError` on startup, which would be frustrating for
users.

"""
import importlib
import logging
import pkgutil
import sys
from pathlib import Path

logging.getLogger(name='docs').getChild('sphinxext').addHandler(logging.StreamHandler())

# How to check the current namespace
if hasattr(locals(), '__path__'):
    __path__ = pkgutil.extend_path(__path__, __name__)
else:
    sys.path.insert(0, str(Path(__file__).resolve()))

# Don't emit an error on IPython startup if not installed.


def ask_for_import(mod, package=None):
    """Import a module and return `None` if it's not found.

    Parameters
    ----------
    mod : str
        Module to import
    package : str, optional
        Package the module is found in.

    Returns
    -------
    imported : mod
        Module as imported by :func:`importlib.import_module`.

    """
    try:
        imported = importlib.import_module(mod, package=package)
    except (ImportError, ModuleNotFoundError):
        pass
    else:
        return imported


ask_for_import('IPython')

if ask_for_import('default_profile'):

    if ask_for_import('sphinx'):
        from default_profile.sphinxext import custom_doctests  # noqa F401
        # from default_profile.sphinxext.ipython_directive import EmbeddedSphinxShell, IPythonDirective  # noqa F401
        from default_profile.sphinxext.magics import LineMagicRole, CellMagicRole  # noqa F401
