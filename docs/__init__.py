import logging

docs_logger = logging.getLogger(name='docs')
docs_logger.setLevel(logging.WARNING)
docs_logger.addHandler(logging.StreamHandler)

import default_profile
