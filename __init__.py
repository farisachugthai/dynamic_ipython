"""
NOQA F401
"""
import logging
from logging import NullHandler
import os
import sys

from IPython import get_ipython

_ip = get_ipython()

logger = logging.getLogger(name=__name__).addHandler(NullHandler)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
