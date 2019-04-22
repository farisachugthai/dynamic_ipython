#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Let's make our test extension a package.

===============
Extensions Init
===============
Still wildly unsure of how to correctly initialize packages but
stuff doesn't break as often so that's a win?


Requires
---------
Python3 and IPython 7+

NOQA F401

"""
import logging
from logging import NullHandler
import os
import sys

import pkg_resources
from IPython import get_ipython

_ip = get_ipython()

logging.getLogger(__name__).addHandler(NullHandler())

pkg_resources.declare_namespace(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
