"""Initialize a debugger profile for IPython."""
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

try:
    import ipdb as pdb
except (ImportError, ModuleNotFoundError):
    import pdb

logging.getLogger(__name__).addHandler(NullHandler())
