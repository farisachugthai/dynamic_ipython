#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize desired parameters for :mod:`pandas` at startup.

.. currentmodule:: pandas_init

.. highlight:: python3

:URL: `https://realpython.com/python-pandas-tricks/#1-configure-options-settings-at-interpreter-startup`_

Pandas Initialization
=====================

.. todo::

    - Also we should do a check that we're on python3.6+ because otherwise,
      we'll crash the interpreter as we invoke an expression with f-strings.


Here's an interesting blurb from pandas/docs/conf.py::

    import pandas as pd
    # This ensures correct rendering on system with console encoding != utf8
    # (windows). It forces pandas to encode its output reprs using utf8
    # wherever the docs are built. The docs' target is the browser, not
    # the console, so this is fine.
    pd.options.display.encoding="utf8"

"""
import logging
import sys

logger = logging.basicConfig(level=logging.WARNING)

try:
    import pandas as pd
except ImportError as e:
    logger.warning("Import error: %s" % e)
    sys.exit()


def start():
    """Define options for :mod:`pandas` startup."""
    options = {
        'display': {
            'max_columns': None,
            'max_colwidth': 25,
            'expand_frame_repr': False,  # Don't wrap to multiple pages
            'max_rows': 30,
            'max_seq_items': 50,
            # Max length of printed sequence 'precision': 4,
            'show_dimensions': False,
            'encoding': 'utf-8',
        },
        'mode': {
            'chained_assignment': None
            # Controls SettingWithCopyWarning
        }
    }

    for category, option in options.items():
        for op, value in option.items():
            pd.set_option(f'{category}.{op}', value)  # Python 3.6+


if __name__ == '__main__':
    if sys.version_info() < (3, 6, 0):
        sys.exit("This module requires Python 3.6+")

    start()
    # Clean up namespace in the interpreter
    del start
