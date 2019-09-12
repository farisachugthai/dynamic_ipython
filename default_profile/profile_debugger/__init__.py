"""Initialize a debugger profile for IPython."""
import logging
import os
import sys
from logging import NullHandler
from pprint import pprint  # noqa F401 not used but nice to have

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

from . import ipd

logging.getLogger(__name__).addHandler(NullHandler())
