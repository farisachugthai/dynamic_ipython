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

from profile_default.util import module_log
from profile_default.util import machine
from profile_default.util import timer

logging.getLogger(__name__).addHandler(NullHandler())
