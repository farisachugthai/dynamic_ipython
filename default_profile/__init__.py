#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

The heart of all IPython and console related code lives here.
"""
import logging

try:
    # these should always be available
    import IPython  # noqa F0401
    from IPython import get_ipython  # noqa F0401
except (ImportError, ModuleNotFoundError):
    pass

# from . import profile_debugger, profile_parallel, sphinxext, startup, util
from .sphinxext import custom_doctests, magics
from .startup import ask_for_import
from .util import module_log, machine, pager2, ipython_get_history

default_log_format = '%(created)f : %(module)s : %(levelname)s : %(message)s'
PROFILE_DEFAULT_LOG = logging.getLogger('default_profile')
PROFILE_DEFAULT_LOG.setLevel(logging.WARNING)
PROFILE_DEFAULT_LOG.addHandler(logging.StreamHandler().setLevel(
    logging.WARNING))
