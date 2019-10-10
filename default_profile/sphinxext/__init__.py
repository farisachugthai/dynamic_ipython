"""Todo: Cleanup."""
import importlib
import pkgutil
import sys
from pathlib import Path

# How to check the current namespace
if hasattr(locals(), '__path__'):
    __path__ = pkgutil.extend_path(__path__, __name__)
else:
    sys.path.insert(0, str(Path(__file__).resolve()))


# Don't emit an error on IPython startup if not installed.


def ask_for_import(mod, package=None):
    try:
        imported = importlib.import_module(mod, package=package)
    except (ImportError, ModuleNotFoundError):
        pass



ask_for_import('IPython')
if ask_for_import('sphinx'):
    from default_profile.sphinxext import configtraits
    from default_profile.sphinxext.magics import LineMagicRole, CellMagicRole
