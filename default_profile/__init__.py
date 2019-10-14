#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

The heart of all IPython and console related code lives here.
"""
import logging

try:
    # these should always be available
    import IPython
    from IPython import get_ipython
except (ImportError, ModuleNotFoundError):
    pass

# from . import profile_debugger, profile_parallel, sphinxext, startup, util

default_log_format = '%(created)f : %(module)s : %(levelname)s : %(message)s'
PROFILE_DEFAULT_LOG = logging.getLogger('default_profile')
PROFILE_DEFAULT_LOG.setLevel(logging.WARNING)
PROFILE_DEFAULT_LOG.addHandler(logging.StreamHandler().setLevel(
    logging.WARNING))
