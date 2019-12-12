import os
import sys
import traceback
import pkg_resources

from IPython.core.getipython import get_ipython

pkg_resources.declare_namespace('.')

try:
    from .unimpaired import TerminallyUnimpaired
except Exception as e:
    traceback.format_exception(e)

def check_sys_path():
    """Because I doubt this is a part of the packages modules."""
    if '' or Path(__file__) not in sys.path:
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))