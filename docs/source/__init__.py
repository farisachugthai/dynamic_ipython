import logging

source_docs_logger = logging.getLogger(name='docs').getChild('source')

import sphinx

# Cross your fingers I guess
import default_profile
from .default_profile import startup
from .sphinx_extensions import *
