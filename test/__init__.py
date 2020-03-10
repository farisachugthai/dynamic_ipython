#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import pkg_resources
import pkgutil
import sys
import unittest

pkg_resources.declare_namespace(__name__)

__path__ = sys.path
__path__ = pkgutil.extend_path(__path__, __name__)

try:
    importlib.import_module("default_profile")
except ImportError:
    pass
