#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the package's test suite."""
import doctest  # noqaF401
import logging
from logging import NullHandler
import os
import sys
import unittest   # noqa F401
import warnings

from IPython import get_ipython, start_ipython
try:
    import nose  # noqa F401
except ImportError as e:
    warnings.warn(str(e))


if __name__ == '__main__':
    _ip = get_ipython()

    if _ip is None:
        _ip = start_ipython()

    logger = logging.getLogger(name=__name__).addHandler(NullHandler)

    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
