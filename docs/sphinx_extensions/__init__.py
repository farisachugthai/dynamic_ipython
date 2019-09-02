"""Todo: Cleanup."""
import importlib
from . import magics


def ask_for_import(mod, package=None):
    try:
        return importlib.import_module(mod, package=package)
    except (ImportError, ModuleNotFoundEdrror):
        pass


ask_for_import('IPython')
ask_for_import('sphinx')
default_profile = ask_for_import('default_profile')
ask_for_import('startup', package=default_profile)
