import logging

docs_logger = logging.getLogger(name='docs')

import profile_default
from profile_default import startup

# Cross your fingers I guess
import .sphinx_extensions

import sphinx
