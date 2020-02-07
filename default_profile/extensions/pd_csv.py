#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from io import StringIO
import sys

from IPython.core.getipython import get_ipython

if sys.version_info() < (3, 7):
    from default_profile import ModuleNotFoundError

try:
    import pandas as pd
except ImportError:
    pd = None


def pd_csv(cell):
    """Read in an :class:`io.StringIO()` and parse it with pandas.

    Parameters
    ----------
    cell : str
        User input.

    Returns
    -------
    df : pandas.DataFrame

    """
    if pd is None:
        return  # should this simply raise?
    sio = StringIO(cell)
    return pd.read_csv(sio)


def load_ipython_extension(ip):
    """This function is called when the extension is loaded.

    It accepts an IPython |ip| instance. We can register the magic
    with the :func:`IPython.core.magics.register_magic_function`
    method.

    Parameters
    -----------
    ip : |ip|

    """
    ip.register_magic_function("pd_csv")
