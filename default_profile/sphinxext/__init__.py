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
from default_profile import ask_for_import
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
ask_for_import('IPython')

# We kinda have to assume we're installed if we're building our docs
if ask_for_import('sphinx'):
    from default_profile.sphinxext import custom_doctests  # noqa F401
    # from default_profile.sphinxext.ipython_directive import EmbeddedSphinxShell, IPythonDirective  # noqa F401
    from default_profile.sphinxext.magics import LineMagicRole, CellMagicRole  # noqa F401
