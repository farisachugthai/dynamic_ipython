#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains a collection of utility scripts.

Generally they're modules that are functionally useful for a user
running IPython interactively, but none of the scripts havet been fleshed out
to the extent that they could be easily changed to IPython extensions.

Currently the module aims to:

#) Create consistent `logging.Logger` objects
#) Make a better pager on Windows
#) Create a collection of classes that can more easily remove
   platform-specific issues that continue to arise.

In addition, configure a module-wide logger by equating `logging.BASIC_FORMAT`
with a pre-determined template string like so::

    >>> logging.BASIC_FORMAT = '%(asctime)s : %(levelname)s : %(message)s'
    >>> UTIL_LOGGER = logging.getLogger('profile_default.util')
    >>> UTIL_LOGGER.setLevel(logging.WARNING)

"""
import logging
import os
import sys
from logging import NullHandler

from profile_default.util import module_log
from profile_default.util import machine
from profile_default.util import timer

logging.BASIC_FORMAT = '%(created)f : %(module)s : %(levelname)s : %(message)s'

UTIL_LOGGER = logging.getLogger('profile_default.util')
UTIL_LOGGER.setLevel(logging.WARNING)
