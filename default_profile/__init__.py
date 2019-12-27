#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

The heart of all IPython and console related code lives here.

Moved ask_for_import up here so we can import it from all of the profiles
below without intermingling.

"""
import importlib
import logging
import sys
from traitlets.config.application import LevelFormatter

default_log_format = "%(module)s %(created)f [ %(name)s ] %(message)s "
PROFILE_DEFAULT_LOG = logging.getLogger(name="default_profile")
PROFILE_DEFAULT_LOG.setLevel(logging.WARNING)
PROFILE_DEFAULT_HANDLER = logging.StreamHandler()
PROFILE_DEFAULT_HANDLER.setLevel(logging.WARNING)
PROFILE_DEFAULT_FORMATTER = logging.Formatter(fmt=default_log_format)
PROFILE_DEFAULT_HANDLER.addFilter(logging.Filterer())
PROFILE_DEFAULT_HANDLER.setFormatter(PROFILE_DEFAULT_FORMATTER)
PROFILE_DEFAULT_LOG.addHandler(PROFILE_DEFAULT_HANDLER)

default_traitlets_log_format = (
    "%(highlevel)s %(created)f %(module)s %(levelname)s  %(message)s"
)
default_formatter = LevelFormatter(fmt=default_traitlets_log_format)


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


class ModuleNotFoundError(ImportError):
    """Try to backport this for python3.6<."""

    __module__ = "builtins"  # for py3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "{}\n{}".format(self.__class__.__name__, self.__traceback__)


# Keep these imports below the ModuleNotFoundError backport
try:
    # these should always be available
    import IPython  # noqa F0401
    from IPython.core.getipython import get_ipython  # noqa F0401
except (ImportError, ModuleNotFoundError):
    pass
