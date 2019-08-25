import logging

docs_logger = logging.getLogger(name='docs')

import profile_default
from profile_default import startup

# Cross your fingers I guess
from .sphinx_extensions import *

import sphinx

# Oh also we need this
import make
from make import DocBuilder
