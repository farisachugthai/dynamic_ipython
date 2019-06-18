#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Requires
---------
Python3 and IPython 7+

"""
import importlib
import logging
from logging import NullHandler
import os
from profile_default.util import module_log
import sys

logging.getLogger(__name__).addHandler(NullHandler())

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

rehashx_mod = importlib.import_module('01_rehashx')

user_aliases = importlib.import_module('20_aliases')
