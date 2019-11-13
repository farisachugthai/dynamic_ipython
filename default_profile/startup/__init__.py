#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Imports all files in this directory by utilizing the
:mod:`importlib` API
to avoid import problems as Python modules can't begin with numbers.

"""
import importlib
import logging
import sys

logging.BASIC_FORMAT = "%(created)f : %(module)s : %(levelname)s : %(message)s"

STARTUP_LOGGER = logging.getLogger(name="default_profile").getChild("startup")
STARTUP_LOGGER.setLevel(logging.WARNING)
STARTUP_HANDLER = logging.StreamHandler(stream=sys.stdout)
STARTUP_HANDLER.setLevel(logging.WARNING)
STARTUP_FORMATTER = logging.Formatter(fmt=logging.BASIC_FORMAT)
STARTUP_FILTERER = logging.Filterer()
STARTUP_HANDLER.addFilter(STARTUP_FILTERER)
STARTUP_HANDLER.setFormatter(STARTUP_FORMATTER)
STARTUP_LOGGER.addHandler(STARTUP_HANDLER)


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


rehashx_mod = importlib.import_module("default_profile.startup.01_rehashx")
easy_import_mod = importlib.import_module("default_profile.startup.04_easy_import")
log_mod = importlib.import_module("default_profile.startup.05_log")
help_helpers_mod = importlib.import_module("default_profile.startup.06_help_helpers")
envvar_mod = importlib.import_module("default_profile.startup.10_envvar")
clipboard_mod = importlib.import_module("default_profile.startup.11_clipboard")
aliases_mod = importlib.import_module("default_profile.startup.20_aliases")
fzf_mod = importlib.import_module("default_profile.startup.21_fzf")
alias_manager_mod = importlib.import_module("default_profile.startup.22_alias_manager")
readline_mod = importlib.import_module("default_profile.startup.30_readline")
yank_last_arg_mod = importlib.import_module("default_profile.startup.31_yank_last_arg")
numpy_init_mod = importlib.import_module("default_profile.startup.41_numpy_init")
pandas_init_mod = importlib.import_module("default_profile.startup.42_pandas_init")
sysexception_mod = importlib.import_module("default_profile.startup.50_sysexception")
