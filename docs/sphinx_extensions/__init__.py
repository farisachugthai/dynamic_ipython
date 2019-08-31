from . import magics
import importlib
import logging


def ask_for_import(mod, package=None):
    """Try/except for importing modules."""
    try:
        return importlib.import_module(mod)
    except (ImportError, ModuleNotFoundError):
        pass


ask_for_import('sphinx')
ask_for_import('IPython')
profile_default = ask_for_import('profile_default')
ask_for_import('startup', package=profile_default)
