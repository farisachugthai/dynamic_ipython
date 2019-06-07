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

from profile_default.util import log
from profile_default.util import machine

_ip = get_ipython()

logging.getLogger(__name__).addHandler(NullHandler())

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
