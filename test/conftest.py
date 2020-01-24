"""Set up pytest."""
import multiprocessing
import os
import sys
import tempfile

from IPython.core.interactiveshell import InteractiveShell

import pytest
from pytest import set_trace

# from pytest.nose import *
from _pytest import nose
from _pytest import unittest

try:
    import default_profile
except:
    sys.exit('Not installed.')
else:
    from default_profile import ask_for_import


def pytest_load_initial_conftests(args):
    """If you have the xdist plugin installed you will now always perform test runs using a number of subprocesses close to your CPU."""
    if "xdist" in sys.modules:  # pytest-xdist plugin

        num = max(multiprocessing.cpu_count() / 2, 1)
        args[:] = ["-n", str(num)] + args


@pytest.fixture(scope="session", autouse=True)
def _ip():
    return InteractiveShell()


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


def pytest_report_header():
    """Try to imitate the nosetests header."""
    # return f"\nMatplotlib:\n {matplotlib in sys.modules}\nPygments:\n {pygments in sys.modules}\nSQLite3:\n {sqlite3 in sys.modules}\n"
    # crashes
    ret = []
    for i in ['matplotlib', 'sqlite3', 'pygments']:
        ask_for_import(i)
        if sys.modules[i]:
            ret.append(i)
    return ret


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed ({})".format(previousfailed.name))


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


ALL = set("darwin linux win32".split())


def pytest_runtest_setup(item):
    """Consider you have a test suite which marks tests for particular platforms.

    Namely pytest.mark.darwin, pytest.mark.win32 etc.
    and you also have tests that run on all platforms and have
    no specific marker. If you now want to have a way to only
    run the tests for your particular platform, you could use
    the following plugin:
    """
    supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
    plat = sys.platform
    if supported_platforms and plat not in supported_platforms:
        pytest.skip("cannot run on platform {}".format(plat))
