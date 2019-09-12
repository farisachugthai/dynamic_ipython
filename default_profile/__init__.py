#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

The heart of all IPython and console related code lives here.
"""
import logging
import os
import sys

try:
    # these should always be available
    import IPython
    from IPython import get_ipython
except (ImportError, ModuleNotFoundError):
    pass

# Are you allowed to do something like this?
# import default_profile
# Because this should be the default_profile package ya know lol
# from default_profile.__about__ import *
# from default_profile.__about__ import __version__
# Which invocation?
# from .__about__ import *  # noqa

from . import extensions, profile_debugger, profile_parallel, sphinxext, startup, util
from .__about__ import __version__
from . import ipython_config
from . import ipython_kernel_config


default_log_format = '%(created)f : %(module)s : %(levelname)s : %(message)s'
PROFILE_DEFAULT_LOG = logging.getLogger('default_profile')
PROFILE_DEFAULT_LOG.setLevel(logging.WARNING)
PROFILE_DEFAULT_LOG.addHandler(logging.StreamHandler().setLevel(logging.WARNING))