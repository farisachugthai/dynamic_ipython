#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import functools
import importlib
import logging
import pkgutil

from importlib.util import _find_spec_from_path

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
    print('default_profile is not a package with __path__ defined.')

BASIC_FORMAT = "[ %(name)s  %(relativeCreated)d ] %(levelname)s %(module)s %(message)s "
STARTUP_LOGGER = logging.getLogger(name=__name__)

STARTUP_HANDLER = logging.StreamHandler()
STARTUP_FORMATTER = logging.Formatter(fmt=BASIC_FORMAT)
STARTUP_FILTERER = logging.Filterer()
STARTUP_HANDLER.addFilter(STARTUP_FILTERER)
STARTUP_HANDLER.setFormatter(STARTUP_FORMATTER)
STARTUP_LOGGER.addHandler(STARTUP_HANDLER)
STARTUP_LOGGER.setLevel(logging.WARNING)


def module_from_path(path):
    """Return a module from a given 'path'.

    Intended as a simpler replacement for the now deprecated importlib.find_module.
    """
    spec = _find_spec_from_path(path)
    try:
        if spec is not None:
            return importlib.util.module_from_spec(spec)
    except ModuleNotFoundError:
        print(path + 'not imported')