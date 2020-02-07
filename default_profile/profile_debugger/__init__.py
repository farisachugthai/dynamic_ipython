"""Initialize a debugger profile for IPython."""
from default_profile import PROFILE_DEFAULT_LOG, QueueHandler
from default_profile import ask_for_import  # noqa F401

debugger_logger = PROFILE_DEFAULT_LOG.getChild()
debugger_logger.addHandler(QueueHandler())
