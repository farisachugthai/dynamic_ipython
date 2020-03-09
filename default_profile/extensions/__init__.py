#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===========
Extensions
===========

This houses a collection of IPython extensions I've written.

"""
import logging

extensions_logger = logging.getLogger(name="default_profile").getChild("extensions")
extensions_handler = logging.StreamHandler()
extensions_handler.setLevel(logging.WARNING)
extensions_handler.setFormatter(
    logging.Formatter(fmt="%(asctime)s %(levelname).4s %(message)s", datefmt="%H:%M:%S")
)

extensions_logger.setLevel(logging.WARNING)
extensions_logger.addHandler(extensions_handler)

# Probably alo worth notin
try:
    from sympy import init_printing

    init_printing()
except ImportError:
    pass
