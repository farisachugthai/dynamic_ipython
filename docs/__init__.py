from pkgutil import extend_path
import logging
import sys

docs_logger = logging.getLogger(name='docs')
docs_logger.setLevel(logging.WARNING)
docs_handler = logging.StreamHandler(sys.stdout)
docs_handler.setLevel(logging.WARNING)
docs_handler.setFormatter(logging.Formatter())
docs_logger.addHandler(docs_handler)

if hasattr(locals(), '__path__'):
    __path__ = extend_path(__path__, __name__)

    print('\nPath is: {}\n'.format(__path__))
else:
    pass
