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



def ask_for_import(mod, package=None):
    try:
        return importlib.import_module(mod, package=package)
    except (ImportError, ModuleNotFoundError):
        pass


ask_for_import('IPython')
ask_for_import('sphinx')
default_profile = ask_for_import('default_profile')
ask_for_import('startup', package=default_profile)

magics = ask_for_import('magics', package='.')
if magics is not None:
    print('magics imported')


make = ask_for_import('make', package='.')
if make is not None:
    print('make imported')
