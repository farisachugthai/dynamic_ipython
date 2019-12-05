"""Set up pytest."""
import os
import tempfile

from IPython import get_ipython
import pytest
# from pytest.nose import *

import default_profile


@pytest.fixture(autouse=True)
def _ip():
    return get_ipython()


def pytest_addoption(parser):
    """The recommended way of marking tests slow."""
    parser.addoption('--slow', action='store_true', default=False, help='run slow tests')


def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: mark test as slow to run')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--slow'):
        # If the option is present, don't skip slow tests.
        return
    skip_slow = pytest.mark.skip(reason='only runs when --slow is set')
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


if _ip is None:
    from IPython import start_ipython
    start_ipython()
