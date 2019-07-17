#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

Requires
---------
Python3 and IPython 7+

05/21/2019:

Commented out IPython because the package dependency in an __init__
file means that an unsuspecting user will try to install and the build
will fail before pip even gets a chance to install the dependencies.

Jul 12, 2019:

Admittedly, you could just use a try/except....

"""
import logging
import os
import sys
from logging import NullHandler

try:
    # these should always be available
    import IPython
    from IPython import get_ipython
except (ImportError, ModuleNotFoundError):
    pass

logging.getLogger(__name__).addHandler(NullHandler())
