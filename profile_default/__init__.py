#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring."""
import logging
import os
import sys

try:
    # these should always be available
    import IPython
    from IPython import get_ipython
except (ImportError, ModuleNotFoundError):
    pass

logging.BASIC_FORMAT = '%(created)f : %(module)s : %(levelname)s : %(message)s'
PROFILE_DEFAULT_LOG = logging.getLogger('profile_default')
PROFILE_DEFAULT_LOG.setLevel(logging.WARNING)
