#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
===================================
IPython-specific Sphinx extensions.
===================================

Imports the modules found in the current directory and utilizes
:mod:`pkgutil` and :func:`pkgutil.extend_path`
to extend the packages ``__path__`` parameter.

It only imports the modules below if this repository has been installed.

If this weren't true, then starting IPython without this package installed
would emit :exc:`ImportError` on startup, which would be frustrating for
users.

"""
import importlib
import logging
import pkgutil
import sys
from logging import Logger
from pathlib import Path

import pkg_resources

from .magics import (
    LineMagicRole,
    CellMagicRole,
)  # noqa F401

sphinxext_logger: Logger = logging.getLogger(name="default_profile").getChild("sphinxext")
sphinxext_formatter = logging.Formatter(datefmt="%H:%M:%S")
sphinxext_handler = logging.StreamHandler()
sphinxext_handler.setFormatter(sphinxext_formatter)
sphinxext_handler.setLevel(logging.WARNING)
sphinxext_logger.addHandler(sphinxext_handler)
sphinxext_logger.setLevel(logging.WARNING)
sphinxext_filter = logging.Filter()
sphinxext_logger.addFilter(sphinxext_filter)

try:
    __path__ = pkgutil.extend_path(__path__, __name__)
except NameError:
    pass
