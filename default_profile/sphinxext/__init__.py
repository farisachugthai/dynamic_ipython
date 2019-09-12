"""Todo: Cleanup."""
import importlib
from pathlib import Path
import pkgutil
import sys

# How to check the current namespace
if hasattr(locals(), '__path__'):
    __path__ = pkgutil.extend_path(__path__, __name__)
else:
    sys.path.insert(0, Path(__file__).resolve())

import default_profile
from default_profile.sphinxext.magics import LineMagicRole, CellMagicRole
from . import configtraits

def ask_for_import(mod, package=None):
    return importlib.import_module(mod, package=package) or None


ask_for_import('IPython')
ask_for_import('sphinx')