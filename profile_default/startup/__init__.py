#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Imports all files in this directory to avoid import problems as
Python modules can't begin with numbers.

Requires
---------
Python3 and IPython 7+

"""
import importlib
import logging
import os
import sys
from logging import NullHandler

from profile_default.util import module_log

logging.getLogger(__name__).addHandler(NullHandler())

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

rehashx_mod = importlib.import_module('01_rehashx')

easy_import = importlib.import_module('04_easy_import')

ipython_file_logger = importlib.import_module('05_log')

help_helpers = importlib.import_module('06_help_helpers')

user_aliases = importlib.import_module('20_aliases')

vi_mode_keybindings = importlib.import_module('32_vi_modes')

numpy_init = importlib.import_module('41_numpy_init')

pandas_init = importlib.import_module('42_pandas_init')

except_hook = importlib.import_module('50_sysexception')
