"""Set up pytest."""
import multiprocessing
import os
import sys
import tempfile

from traitlets.config import Config
from IPython.core.getipython import get_ipython
from IPython import start_ipython

# from IPython.terminal.ipapp import TerminalIPythonApp

import pytest
from pytest import set_trace

# from pytest.nose import *
from _pytest import nose
from _pytest import unittest

import default_profile


def pytest_load_initial_conftests(args):
    """If you have the xdist plugin installed you will now always perform test runs using a number of subprocesses close to your CPU."""
    if "xdist" in sys.modules:  # pytest-xdist plugin

        num = max(multiprocessing.cpu_count() / 2, 1)
        args[:] = ["-n", str(num)] + args


@pytest.fixture(scope="session", autouse=True)
def _ip():
    # config = Config()
    c = get_ipython()
    # if c is None:
    #     c = startconfigython()
    set_trace()
    c.colors = "NoColor"
    c.term_title = (False,)
    c.autocall = 0
    f = tempfile.NamedTemporaryFile(suffix=u"test_hist.sqlite", delete=False)
    c.HistoryManager.hist_file = f.name
    f.close()
    c.HistoryManager.db_cache_size = 10000
    return c


def pytest_addoption(parser):
    """The recommended way of marking tests slow."""
    parser.addoption(
        "--slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--slow"):
        # If the option is present, don't skip slow tests.
        return
    skip_slow = pytest.mark.skip(reason="only runs when --slow is set")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_report_header(config):
    """Present a custom header. Did this wrong because mpl is installed."""
    return "\nMatplotlib: {}\nSQLite3: {}\n".format(
        ("matplotlib" in sys.modules), ("sqlite3" in sys.modules)
    )


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
