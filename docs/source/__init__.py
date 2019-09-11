import sphinx
import logging
from pathlib import Path
import pkgutil


if hasattr(locals(), '__path__'):
    __path__ = pkgutil.extend_path(__path, __name__)
else:
    sys.path.insert(0, Path(__file__).resolve())


source_docs_logger = logging.getLogger(name='docs').getChild('source')
