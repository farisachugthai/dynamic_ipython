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

from importlib.util import find_spec
from importlib.machinery import SourceFileLoader, FileFinder
from importlib.resources import Package, Resource

import default_profile
from default_profile import QueueHandler

BASIC_FORMAT = default_profile.default_log_format

STARTUP_LOGGER = logging.getLogger(name=__name__)

STARTUP_HANDLER = logging.StreamHandler()
STARTUP_FORMATTER = logging.Formatter(fmt=BASIC_FORMAT)
STARTUP_FILTERER = logging.Filterer()
STARTUP_HANDLER.addFilter(STARTUP_FILTERER)
STARTUP_HANDLER.setFormatter(STARTUP_FORMATTER)
STARTUP_LOGGER.addHandler(STARTUP_HANDLER)
STARTUP_LOGGER.setLevel(logging.WARNING)

rehashx_mod = importlib.import_module("default_profile.startup.01_rehashx")
log_mod = importlib.import_module("default_profile.startup.05_log")
help_helpers_mod = importlib.import_module("default_profile.startup.06_help_helpers")

envvar_mod = importlib.import_module("default_profile.startup.10_envvar")
clipboard_mod = importlib.import_module("default_profile.startup.11_clipboard")

aliases_mod = importlib.import_module("default_profile.startup.20_aliases")
fzf_mod = importlib.import_module("default_profile.startup.21_fzf")

readline_mod = importlib.import_module("default_profile.startup.30_readline")
# yank_last_arg_mod = importlib.import_module("default_profile.startup.31_yank_last_arg")
# kb_mod = importlib.import_module("default_profile.startup.32_kb")
# bottom_toolbar_mod = importlib.import_module(
#     "default_profile.startup.33_bottom_toolbar"
# )
# completion_mod = importlib.import_module("default_profile.startup.34_completion")

numpy_init_mod = importlib.import_module("default_profile.startup.41_numpy_init")

try:
    import repralias
    from repralias import ReprAlias
except ImportError:
    pass
# import pygit
# import event_loops


class UsageError(Exception):
    def __init__(self, err=None, *args, **kwargs):
        self.err = err
        super().__init__(self, *args, **kwargs)

    def __repr__(self):
        return "{}\t \t{}".format(self.__class__.__name__, self.err)

    def __call__(self, err):
        return self.__repr__(err)
