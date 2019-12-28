#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the whole repository.

Now we're getting into the weird parts of how Python distributes things
and I'm beginning to question whether I need to make a setuptools.Distribution
or a namespace package or any of the 1000 ways you can do this.

Running the below in the ``git rev-parse --show-prefix == .`` showed some
good signs though::

>>> import pkg_resources
>>> for i in pkg_resources.find_distributions('.'):
...     print(i)
...
dynamic-ipython 0.0.1

Also a good check to see whats being counted as a package is:

>>> from setuptools import find_packages, find_namespace_packages
>>> found_packages = find_packages(where='.')
>>> found_namespace_packages = find_namespace_packages(where='.')
>>> logging.debug('Found packages were: {}'.format(found_packages))
>>> logging.debug('Found namespace packages were: {}'.format(found_namespace_packages))

Unfortunately I'm not getting any log messages when I start up here so thats
indicating to me none of these lines run. Why is that?

"""
import logging
import os
import pkgutil

# from pkg_resources import declare_namespace
from setuptools import find_packages, find_namespace_packages
import sys

try:  # new replacement for the pkg_resources API
    import importlib_metadata
except ImportError:
    importlib_metadata = None


import default_profile
from default_profile.__about__ import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# This kills everything on termux and makes run pytest or tox in the root
# of this repo impossible. hmmmmm.
# declare_namespace(REPO_ROOT)

found_packages = find_packages(where=".")
found_namespace_packages = find_namespace_packages(where=".")

logging.debug("Found packages were: {}".format(found_packages))
logging.debug("Found namespace packages were: {}".format(found_namespace_packages))

logging.debug("Sys.path before:" + str(sys.path))
sys.path = sys.path + [REPO_ROOT]
logging.debug("Sys path after:" + str(sys.path))

if hasattr(locals(), "__path__"):
    ___path__ = pkgutil.extend_path(__path__, __name__)
