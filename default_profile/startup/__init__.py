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

STARTUP_LOGGER = logging.getLogger(name=__name__).getChild("startup")

# STARTUP_HANDLER = QueueHandler()
STARTUP_HANDLER = logging.StreamHandler()
STARTUP_FORMATTER = logging.Formatter(fmt=BASIC_FORMAT)
STARTUP_FILTERER = logging.Filterer()
STARTUP_HANDLER.addFilter(STARTUP_FILTERER)
STARTUP_HANDLER.setFormatter(STARTUP_FORMATTER)
STARTUP_LOGGER.addHandler(STARTUP_HANDLER)
STARTUP_LOGGER.setLevel(logging.WARNING)

# rehashx_mod = importlib.import_module('default_profile.startup.01_rehashx')

# rehashx_mod = importlib.import_module("01_rehashx", package="default_profile.startup")

# log_mod = importlib.import_module("05_log", package="default_profile.startup")

# help_helpers_mod = importlib.import_module(
#     "06_help_helpers", package="default_profile.startup"
# )

# envvar_mod = importlib.import_module("10_envvar", package="default_profile.startup")

# clipboard_mod = importlib.import_module(
#     "11_clipboard", package="default_profile.startup"
# )

# aliases_mod = importlib.import_module("20_aliases", package="default_profile.startup")

# fzf_mod = importlib.import_module("21_fzf", package="default_profile.startup")

# readline_mod = importlib.import_module("30_readline", package="default_profile.startup")

# yank_last_arg_mod = importlib.import_module(
#     "31_yank_last_arg", package="default_profile.startup"
# )

# kb_mod = importlib.import_module("32_kb", package="default_profile.startup")

# bottom_toolbar_mod = importlib.import_module(
#     "33_bottom_toolbar", package="default_profile.startup"
# )

completion_mod = importlib.import_module("default_profile.startup.34_completion")

numpy_init_mod = importlib.import_module("default_profile.startup.41_numpy_init")

try:
    import repralias
    from repralias import ReprAlias
except ImportError:
    pass
# import pygit
# import event_loops
