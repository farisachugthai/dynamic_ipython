"""Set up pytest."""

from IPython import get_ipython
import pytest
# from pytest.nose import *

import default_profile


@pytest.fixture(scope='session')
def _ip():
   return get_ipython()


if _ip is None:
   from IPython import start_ipython
   start_ipython()