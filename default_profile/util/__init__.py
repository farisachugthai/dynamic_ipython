#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========
Utilities
==========

The modules contained in this package are, generally speaking, a collection of
scripts that I've found useful while working with IPython, but that unfortunately
haven't been fleshed out enough.

They're still all useful in their current state and when the user is
running IPython interactively, but none of the scripts havet been fleshed out
to the extent that they could be easily changed to IPython extensions.

Goals
=====

Currently the module aims to:

#) Create consistent `logging.Logger` objects
#) Make a better pager on Windows
#) Create a collection of classes that can more easily remove
   platform-specific issues that continue to arise.

In addition, configure a module-wide logger by equating `logging.BASIC_FORMAT`
with a pre-determined template string like so::

    >>> logging.BASIC_FORMAT = '%(asctime)s : %(levelname)s : %(message)s'
    >>> UTIL_LOGGER = logging.getLogger('default_profile.util')
    >>> UTIL_LOGGER.setLevel(logging.WARNING)

"""
import logging

from .copytree import CopyTree
from .ipython_get_history import get_history
from .machine import Platform
from .module_log import stream_logger
from .paths import _path_build, PathValidator
from .pager2 import c
from .profile_override import ReprProfileDir
from .timer import timer as _itimer

logging.BASIC_FORMAT = '%(created)f : %(module)s : %(levelname)s : %(message)s'

UTIL_LOGGER = logging.getLogger('default_profile').getChild('util')
UTIL_LOGGER.setLevel(logging.WARNING)
util_handler = logging.StreamHandler()
util_formmatter = logging.Formatter(fmt=logging.BASIC_FORMAT)
util_handler.setLevel(logging.WARNING)
UTIL_LOGGER.addHandler(util_handler)
