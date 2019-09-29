#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Imports all files in this directory by utilizing the :mod:`importlib` API
to avoid import problems as Python modules can't begin with numbers.
"""
import default_profile
import importlib
import logging
import os
import sys
from logging import NullHandler

import traitlets
from traitlets.config import Config, get_config
import IPython
from IPython import get_ipython
from IPython.core.error import UsageError

# _ip = get_ipython()

# Don't do this because it'll cause Sphinx to raise an error and the docs
# won't build
# if not _ip:
#     raise UsageError('IPython not successfully started.')

# from default_profile.util import module_log

logging.BASIC_FORMAT = '%(created)f : %(module)s : %(levelname)s : %(message)s'

STARTUP_LOGGER = logging.getLogger('default_profile').getChild('startup')
STARTUP_LOGGER.setLevel(logging.WARNING)

rehashx_mod = importlib.import_module('default_profile.startup.01_rehashx')

easy_import_mod = importlib.import_module(
    'default_profile.startup.04_easy_import'
)

ipython_file_logger = importlib.import_module('default_profile.startup.05_log')

help_helpers = importlib.import_module(
    'default_profile.startup.06_help_helpers'
)

aliases_mod = importlib.import_module('default_profile.startup.20_aliases')
numpy_init = importlib.import_module('default_profile.startup.41_numpy_init')
pandas_init = importlib.import_module('default_profile.startup.42_pandas_init')

except_hook = importlib.import_module(
    'default_profile.startup.50_sysexception'
)
