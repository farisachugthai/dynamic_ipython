#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize desired parameters for :mod:`pandas` at startup.

=====================
Pandas Initialization
=====================

.. module:: 42_pandas_init
    :synopsis: Set display options for pandas.

.. highlight:: ipython

:URL: https://realpython.com/python-pandas-tricks/#1-configure-options-settings-at-interpreter-startup

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

from profile_default.util import module_log


def pandas_init():
    """Define options for :mod:`pandas` startup.

    .. tip::

        Don't set `start.options['show_dimensions'] to ``False``.
        ``'show_dimensions'`` means show the size of the `pd.DataFrame` object.

        ``truncate`` indicates to only display it when the DataFrame is...
        well truncated. [1]

        .. [1] https://pandas.pydata.org/pandas-docs/stable/user-guide/options.html

    """
    options = {
        'display': {
            'encoding': 'utf-8',
            'expand_frame_repr': False,  # Don't wrap to multiple pages
            'html.table_schema': True,
            'max_columns': None,
            'max_colwidth': 25,
            'max_rows': 30,
            'max_seq_items': 50,
            # Max length of printed sequence 'precision': 4,
            'show_dimensions': 'truncate',
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
    if sys.version_info < (3, 6, 0):
        sys.exit("This module requires Python 3.6+")

    log = logging.getLogger(name='profile_default.startup.pandas_init')
    PANDAS_LOGGER = module_log.stream_logger(logger=log, log_level=logging.INFO)

    try:
        import pandas as pd
    except (ImportError, ModuleNotFoundError) as e:
        # jesus christ this just printed the error like 8 times. need to fix
        # LOGGER.warning("Import error: %s" % e, exc_info=1)
        # sys.exit()
        PANDAS_LOGGER.warning("Import error: %s", e)
    else:
        pandas_init()
