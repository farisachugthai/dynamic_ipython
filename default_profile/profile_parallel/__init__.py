"""
===========
IPyParallel
===========

.. currentmodule:: ipyparallel

Initialize a IPyParallel profile for IPython.

"""
import logging
import os
import sys
from logging import NullHandler

try:
    # these should always be available
    import IPython
    from IPython import get_ipython
except (ImportError, ModuleNotFoundError):
    pass

try:
    import ipdb as pdb
except (ImportError, ModuleNotFoundError):
    import pdb

logging.basicConfig(level=logging.WARNING)

try:
    import ipyparallel
except (ImportError, ModuleNotFoundError) as e:
    logging.warning(e)

import default_profile

from . import ipcluster_config, ipcontroller_config, ipengine_config
