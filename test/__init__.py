#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Requires
---------
Python3 and IPython 7+

"""
import logging
from logging import NullHandler
import os
import sys

from IPython import get_ipython, start_ipython

_ip = get_ipython()

if _ip is None:
    _ip = start_ipython()

logger = logging.getLogger(name=__name__).addHandler(NullHandler)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
