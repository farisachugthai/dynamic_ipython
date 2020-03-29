#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

sphinxext_logger: Logger = logging.getLogger(name="default_profile").getChild(
    "sphinxext"
)
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
