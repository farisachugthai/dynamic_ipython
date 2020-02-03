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

from . import cwd_prompt, example
from .event_watcher_example import VarWatcher
from .job_control import install
from .pd_csv import pd_csv
from .termux_clipboard import ClipboardMagics

extensions_logger = logging.getLogger(name="default_profile").getChild("extensions")
extensions_handler = logging.StreamHandler()
extensions_handler.setLevel(logging.WARNING)
extensions_handler.setFormatter(logging.Formatter())
extensions_logger.setLevel(logging.WARNING)
extensions_logger.addHandler(extensions_handler)