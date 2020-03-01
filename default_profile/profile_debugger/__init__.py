"""Initialize a debugger profile for IPython."""
from . import debug
import logging
import queue

from default_profile import QueueHandler
from default_profile import ask_for_import  # noqa F401

debugger_logger = logging.getLogger(name="default_profile").getChild("profile_debugger")

debugger_queue_handler = QueueHandler(queue.SimpleQueue())
debugger_queue_handler.setLevel(logging.INFO)
debugger_logger.addHandler(debugger_queue_handler)
debugger_logger.setLevel(logging.INFO)
debugger_logger.addFilter(logging.Filter(name="default_profile.profile_debugger"))
