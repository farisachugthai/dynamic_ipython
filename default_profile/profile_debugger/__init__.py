"""Initialize a debugger profile for IPython."""
import logging
from logging import StreamHandler

from . import ipd, ipdb3

debugger_logger = logging.getLogger(__name__).addHandler(StreamHandler())
