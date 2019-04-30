import logging
import sys

from IPython import get_ipython
from IPython.core.magic import line_magic

logging.getLogger(name=__name__)


@line_magic
def load_ext(module_str, shell=None):
    """Load an IPython extension by its module name."""
    if not module_str:
        raise RuntimeError('Missing module name.')
        res = _ip.extension_manager.load_extension(module_str)
        if res == 'already loaded':
            logging.warning("The %s extension is already loaded. To reload it, use:" % module_str)
            print("%reload_ext", module_str)

        elif res == 'no load function':
            logging.error("The %s module is not an IPython extension." % module_str)


if __name__ == "__main__":
    _ip = get_ipython()
    args = sys.argv[1:]
    if len(args) == 0:
        sys.exit('E127')
    elif len(args) > 0:
        for i in args:
            module_str = sys.argv[i]
            load_ext(module_str, shell=_ip)
    else:
        raise IndexError
