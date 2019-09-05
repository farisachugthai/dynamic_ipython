import logging
import sys

docs_logger = logging.getLogger(name='docs')
docs_logger.setLevel(logging.WARNING)
docs_handler = logging.StreamHandler(sys.stdout)
docs_handler.setLevel(logging.WARNING)
docs_logger.addHandler(docs_handler)

import default_profile

try:
    from .sphinx_extensions import make
except Exception as e:
    docs_logger.error(e, sys.exc_info=1)
