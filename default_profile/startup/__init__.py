#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Imports all files in this directory by utilizing the
:mod:`importlib` API
to avoid import problems as Python modules can't begin with numbers.

Define `UsageError` as well as that needed to be redefined from IPython,
and is used frequently enough to warrant being in the package's ``__init__``.
"""
# import functools
import importlib
import logging

# noinspection PyProtectedMember
from importlib.util import _find_spec_from_path
import os
import pkgutil
import sys

try:
    from importlib.machinery import SourceFileLoader, FileFinder
except ImportError:
    SourceFileLoader = FileFinder = None

try:
    from importlib.resources import Package, Resource
except ImportError:
    Package = Resource = None

try:
    __path__ = pkgutil.extend_path(__path__, __name__)
except NameError:
    pass

BASIC_FORMAT = "[ %(name)s  %(relativeCreated)d ] %(levelname)s %(module)s %(message)s "
STARTUP_LOGGER = logging.getLogger(name=__name__)

STARTUP_HANDLER = logging.StreamHandler()
STARTUP_FORMATTER = logging.Formatter(fmt=BASIC_FORMAT)
STARTUP_FILTERER = logging.Filterer()
STARTUP_HANDLER.addFilter(STARTUP_FILTERER)
STARTUP_HANDLER.setFormatter(STARTUP_FORMATTER)
STARTUP_LOGGER.addHandler(STARTUP_HANDLER)
STARTUP_LOGGER.setLevel(logging.WARNING)

# imp = functools.partial(importlib.util.module_from_spec importlib.util.module_from_spec(_find_spec_from_path))


class UsageError(Exception):
    def __init__(self, err=None, *args, **kwargs):
        self.err = err
        super().__init__(self, *args)

    def __repr__(self):
        return "{}\t \t{}".format(self.__class__.__name__, self.err)

    def __call__(self, err):
        return self.__repr__()


def module_from_path(path):
    # XXX: This is gonna get really ugly really fast
    spec = _find_spec_from_path(path)
    try:
        if spec is not None:
            return importlib.util.module_from_spec(spec)
    except ModuleNotFoundError:
        pass


# returned none
# rehashx_mod = module_from_path("01_rehashx")

rehashx_mod = module_from_path("default_profile.startup.01_rehashx")

log_mod = module_from_path("default_profile.startup.05_log")

help_helpers_mod = module_from_path("default_profile.startup.06_help_helpers")
envvar_mod = module_from_path("default_profile.startup.10_envvar")
clipboard_mod = module_from_path("default_profile.startup.11_clipboard")
aliases_mod = module_from_path("default_profile.startup.20_aliases")
_fzf_spec = _find_spec_from_path("default_profile.startup.fzf")
if _fzf_spec is not None:
    fzf_mod = importlib.util.module_from_spec(_fzf_spec)

tmux_mod = module_from_path("default_profile.startup.tmux")

readline_mod = module_from_path("default_profile.startup.30_readline")
kb_mod = module_from_path("default_profile.startup.32_kb")
bottom_toolbar_mod = module_from_path("default_profile.startup.33_bottom_toolbar")
lexer_mod = module_from_path("default_profile.startup.35_lexer")
numpy_init_mod = module_from_path("default_profile.startup.41_numpy_init")
completions_mod = module_from_path("default_profile.startup.completions")
event_loop_mod = module_from_path("default_profile.startup.event_loops")
pygit_mod = module_from_path("default_profile.startup.pygit")
repralias_mod = module_from_path("default_profile.startup.repralias")
