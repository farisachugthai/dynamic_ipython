"""Todo: Cleanup."""
import importlib
from pathlib import Path
import pkgutil
import sys

# How to check the current namespace
if hasattr(locals(), '__path__'):
    __path__ = pkgutil.extend_path(__path, __name__)
else:
    sys.path.insert(0, Path(__file__).resolve())

import default_profile
import default_profile.sphinxext.magics
from default_profile.sphinxext.magics import LineMagicRole, CellMagicRole


def ask_for_import(mod, package=None):
    return importlib.import_module(mod, package=package) or None


ask_for_import('IPython')
ask_for_import('sphinx')
# default_profile = ask_for_import('default_profile')
# ask_for_import('startup', package=default_profile)

# magics = ask_for_import('magics', package='.')
# if magics is not None:
#     print('magics imported')


# make = ask_for_import('make', package='.')
# if make is not None:
#     print('make imported')
