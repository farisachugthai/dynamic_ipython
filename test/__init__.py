#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the package's test suite.

:date: 09/04/2019

On a positive note, the debug logging informed me that your sys.path mods
are actually making their way across the package. The LogRecords just showed
up while I was playing around with the configurations for
unittest in PyCharm.

.. ipython::
    :verbatim:

    root: DEBUG: Found packages were: []
    root: DEBUG: Found namespace packages were: []
    root: DEBUG: Sys.path before:[
    '/home/faris/projects',
    '/home/faris/projects/dynamic_ipython',
]


"""
import doctest
import logging
import os
import sys
import unittest
import warnings

import IPython
from IPython import get_ipython

try:
    import nose  # noqa F401
    import default_profile
except Exception as e:
    warnings.warn(e)


def setup_test_logging():
    """Set up some logging so we can see what's happening."""
    logger = logging.getLogger(name=__name__)
    test_handler = logging.StreamHandler(stream=sys.stdout)
    test_formatter = logging.Formatter(
        fmt="%(created)f : %(module)s : %(levelname)s : %(message)s"
    )
    test_handler.setFormatter(test_formatter)
    test_handler.setLevel(logging.WARNING)
    logger.setLevel(logging.WARNING)
    logger.addHandler(test_handler)
    return logger


if __name__ == "__main__":
    test_logger = setup_test_logging()
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    doctest_finder = doctest.DocTestFinder()
    unittest.main()
    doctest.DocTestSuite("__main__", globs="*")
