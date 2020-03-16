#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib

importlib.invalidate_caches()

try:
    default_profile = importlib.import_module("default_profile")
except ImportError:
    pass


try:
    from test import *  # noqa
    # so we can have their namespace too
except ImportError:
    pass
