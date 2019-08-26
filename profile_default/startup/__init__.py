#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Imports all files in this directory by utilizing the :mod:`importlib` API
to avoid import problems as Python modules can't begin with numbers.
"""
import importlib
import logging
import os
import sys
from logging import NullHandler

import profile_default
import traitlets
from traitlets.config import Config, get_config
import IPython
from IPython import get_ipython
from IPython.core.error import UsageError

_ip = get_ipython()

# Don't do this because it'll cause Sphinx to raise an error and the docs
# won't build
# if not _ip:
#     raise UsageError('IPython not successfully started.')

from profile_default.util import module_log

logging.BASIC_FORMAT = '%(created)f : %(module)s : %(levelname)s : %(message)s'

STARTUP_LOGGER = logging.getLogger('profile_default.startup')
STARTUP_LOGGER.setLevel(logging.WARNING)

rehashx_mod = importlib.import_module('profile_default.startup.01_rehashx')
# Actually really useful when building docs so leave the sys.path hack
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

easy_import = importlib.import_module('profile_default.startup.04_easy_import')
ipython_file_logger = importlib.import_module('profile_default.startup.05_log')
help_helpers = importlib.import_module('profile_default.startup.06_help_helpers')
user_aliases = importlib.import_module('profile_default.startup.20_aliases')
numpy_init = importlib.import_module('profile_default.startup.41_numpy_init')
pandas_init = importlib.import_module('profile_default.startup.42_pandas_init')
except_hook = importlib.import_module('profile_default.startup.50_sysexception')
