#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set some print options for :mod:`numpy`.

==========
Numpy Init
==========

.. currentmodule:: 41_numpy_init

This could be a starting point for practicing module configuration with traits.

"""
import sys

try:
    import numpy as np
except (ImportError, ModuleNotFoundError):
    sys.exit()
