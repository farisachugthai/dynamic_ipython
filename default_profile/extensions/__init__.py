#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===========
Extensions
===========

This houses a collection of IPython extensions I've written.

Many are still works in progress.


"""
import logging
import os
import sys
from logging import NullHandler

extensions_logger = logging.getLogger(name='default_profile'
                                      ).getChild('extensions')
extensions_handler = logging.StreamHandler()
extensions_handler.setLevel(logging.WARNING)
extensions_handler.setFormatter(logging.Formatter())
extensions_logger.setLevel(logging.WARNING)
extensions_logger.addHandler(extensions_handler)

from .event_watcher_example import VarWatcher
from .extension_inspect import PrettyColorfulInspector
from .pd_csv import pd_csv
from .termux_clipboard import termux_clipboard_get

try:
    from . import repr_requests
except Exception as e:
    print(e)
