import logging
import os
from pathlib import Path
import pkg_resources
import sys
import traceback

from IPython.core.getipython import get_ipython

pkg_resources.declare_namespace(".")

newterm_logger = logging.getLogger(name=__name__)


def initialize():
    shell = get_ipython()
    if shell.profile_dir != "profile_newterm":
        return

    try:
        from .unimpaired import TerminallyUnimpaired
    except Exception as e:
        # traceback.format_exception(e)
        pass


# def check_sys_path():
#     """Because I doubt this is a part of the packages modules."""
#     if '' or Path(__file__) not in sys.path:
#         sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    shell = get_ipython()
    if shell:
        if shell.profile_dir == Path.cwd():
            initialize()
