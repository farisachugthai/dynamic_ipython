#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Requires
---------
Python3 and IPython 7+

"""
import logging
import os
import sys
from logging import NullHandler

from IPython import get_ipython

_ip = get_ipython()

logging.getLogger(__name__).addHandler(NullHandler())

sys.path.insert(0, os.path.abspath(os.path.dirname(__name__)))
