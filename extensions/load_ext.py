import logging
import sys

from IPython import get_ipython
from IPython.core.magic import line_magic

logging.getLogger(level=logging.WARNING)


@line_magic
def load_ext(module_str, shell=None):
    """Load an IPython extension by its module name."""
    if not module_str:
        raise UsageError('Missing module name.')
        res = _ip.extension_manager.load_extension(module_str)
        if res == 'already loaded':
            logging.warning("The %s extension is already loaded. To reload it, use:" % module_str)
            logging.warning("%reload_ext", module_str)

        elif res == 'no load function':
            logging.error("The %s module is not an IPython extension." % module_str)


if __name__ == "__main__":
    _ip = get_ipython()
    module_str = sys.argv[1]
    load_ext(module_str, shell=_ip)
