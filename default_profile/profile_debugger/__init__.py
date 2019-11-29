"""Initialize a debugger profile for IPython."""
import logging
from logging import StreamHandler

from default_profile.profile_debugger.ipd import IPD
from . import debug

debugger_logger = logging.getLogger(__name__).addHandler(StreamHandler())
