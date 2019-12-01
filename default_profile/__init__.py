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

from . import profile_newterm
from .profile_newterm import unimpaired

# from . import profile_debugger, profile_parallel, sphinxext, startup, util
from .sphinxext import custom_doctests, magics
from .startup import ask_for_import
# from .util import module_log, machine, pager2, ipython_get_history

default_log_format = '%(created)f : %(module)s : %(levelname)s : %(message)s'
PROFILE_DEFAULT_LOG = logging.getLogger(name='default_profile')
PROFILE_DEFAULT_LOG.setLevel(logging.WARNING)
PROFILE_DEFAULT_HANDLER = logging.StreamHandler()
PROFILE_DEFAULT_HANDLER.setLevel(logging.WARNING)
PROFILE_DEFAULT_FORMATTER = logging.Formatter(fmt=default_log_format)
PROFILE_DEFAULT_HANDLER.addFilter(logging.Filterer())
# PROFILE_DEFAULT_LOG
