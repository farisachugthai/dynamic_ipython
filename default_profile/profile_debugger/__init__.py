"""Initialize a debugger profile for IPython."""
import logging

from default_profile import QueueHandler
from default_profile import ask_for_import  # noqa F401

debugger_logger = logging.getLogger(name="default_profile").getChild("profile_debugger")

debugger_logger.addHandler(QueueHandler())
