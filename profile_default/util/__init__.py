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

logging.getLogger(__name__).addHandler(NullHandler())

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
