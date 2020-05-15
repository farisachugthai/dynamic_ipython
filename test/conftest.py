"""Set up pytest."""
import importlib
import multiprocessing
import os
import sys
import tempfile
from pathlib import Path
from warnings import simplefilter

import IPython
from IPython.testing.globalipapp import get_ipython, start_ipython
from IPython.core.interactiveshell import InteractiveShell

import pytest
from pytest import set_trace

from _pytest.nose import *
from _pytest.unittest import *

# NOTE: marker
# pytest.mark.skipif
# skipif('sys.platform == "win32"'

try:
    import default_profile
except ImportError:
    sys.exit("Not installed.")

simplefilter("ignore", category=DeprecationWarning)
simplefilter("ignore", category=PendingDeprecationWarning)


def setup_module():
    start_ipython()


def pytest_load_initial_conftests(args):
    """If you have the xdist plugin installed you will now always perform test runs using a number of subprocesses close to your CPU."""
    if "xdist" in sys.modules:  # pytest-xdist plugin

        num = max(multiprocessing.cpu_count() / 2, 1)
        args[:] = ["-n", str(num)] + args


@pytest.fixture(scope="session", autouse=True)
def _ip():
    # return InteractiveShell()
    return get_ipython()


@pytest.fixture(scope="session")
def get_session():
    return get_ipython().pt_app


@pytest.fixture(scope="session")
def get_app():
    return get_ipython().pt_app


def pytest_addoption(parser):
    """The recommended way of marking tests slow."""
    parser.addoption(
        "--slow", action="store_true", default=False, help="run slow tests"
    )
    # juat nabbed a whole bunch of stuff from numpy
    parser.addoption(
        "--available-memory",
        action="store",
        default=None,
        help=(
            "Set amount of memory available for running the "
            "test suite. This can result to tests requiring "
            "especially large amounts of memory to be skipped. "
            "Equivalent to setting environment variable "
            "NPY_AVAILABLE_MEM. Default: determined"
            "automatically."
        ),
    )


def pytest_sessionstart(session):
    available_mem = session.config.getoption("available_memory")
    if available_mem is not None:
        os.environ["NPY_AVAILABLE_MEM"] = available_mem


# def pytest_cmdline_preparse(config, args):
#     args[:] = ["--no-success-flaky-report", "--no-flaky-report"] + args


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "valgrind_error: Tests that are known to error under valgrind."
    )
    config.addinivalue_line(
        "markers", "leaks_references: Tests that are known to leak references."
    )
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
    print("IPython %s" % IPython.__version__)

    ret = []
    for i in ["matplotlib", "sqlite3", "pygments"]:
        try:
            if sys.modules[i]:
                ret.append(i)
        except KeyError:
            importlib.invalidate_caches()
            importlib.import_module(i)

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


@pytest.fixture
def cleandir():
    """Return a dir as given by mkdtemp and chdir to it."""
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture
def tmpPath(tmpdir):
    """Return a pytest tmpdir wrapped with a Path class."""
    return Path(tmpdir)


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


class Option:
    """Create a new class for pytest options."""

    def __init__(self, verbosity=0):
        """Initialize with optional parameter for verbosity."""
        self.verbosity = verbosity

    @property
    def args(self):
        values = ["--verbosity=%d" % self.verbosity]
        return values


@pytest.fixture(
    params=[Option(verbosity=0), Option(verbosity=1), Option(verbosity=-1)],
    ids=["default", "verbose", "quiet"],
)
def option(request):
    return request.param


def test_foo(pytestconfig):
    """Session-scoped fixture that returns the :class:`_pytest.config.Config` object."""
    if pytestconfig.getoption("verbose") > 0:
        pass


@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    # doctest_namespace['np'] = numpy
    doctest_namespace["_ip"] = get_ipython()
