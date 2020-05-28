#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import functools
__package__ = "default_profile.startup"
import importlib
import logging
import os

from importlib.util import _find_spec_from_path
from typing import Union, AnyStr


BASIC_FORMAT = "[ %(name)s  %(relativeCreated)d ] %(levelname)s %(module)s %(message)s "
STARTUP_LOGGER = logging.getLogger(name=__name__)

STARTUP_HANDLER = logging.StreamHandler()
STARTUP_FORMATTER = logging.Formatter(fmt=BASIC_FORMAT)
STARTUP_FILTERER = logging.Filterer()
STARTUP_HANDLER.addFilter(STARTUP_FILTERER)
STARTUP_HANDLER.setFormatter(STARTUP_FORMATTER)
STARTUP_LOGGER.addHandler(STARTUP_HANDLER)
STARTUP_LOGGER.setLevel(logging.WARNING)


def module_from_path(path: Union[AnyStr, os.PathLike]):
    """Return a module from a given 'path'.

    Intended as a simpler replacement for the now deprecated importlib.find_module.
    """
    spec = _find_spec_from_path(path)
    try:
        if spec is not None:
            return importlib.util.module_from_spec(spec)
    except ModuleNotFoundError:
        print(path + 'not imported')
