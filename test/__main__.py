"""Create a single entry point for the test suite."""
import argparse
import doctest
import importlib
import logging
import os
import sys
import unittest
import warnings
from doctest import testmod, testfile
from unittest.suite import TestSuite

from unittest.loader import TestLoader, defaultTestLoader, findTestCases

import IPython

# don't forget about this as it may come in handy
# from IPython.lib.deepreload import reload
from IPython.testing.tools import get_ipython_cmd
from IPython import get_ipython

try:
    import nose  # noqa F401
except ImportError as e:
    print(e)

try:
    import pytest
except ImportError:
    warnings.warn("No Pytest. Using unittest.")
    pytest = None

import default_profile


def _parse():
    parser = argparse.ArgumentParser(description="doctest runner")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="print very verbose output for all tests",
    )
    parser.add_argument(
        "-o",
        "--option",
        action="append",
        choices=doctest.OPTIONFLAGS_BY_NAME.keys(),
        default=[],
        help=(
            "specify a doctest option flag to apply"
            " to the test run; may be specified more"
            " than once to apply multiple options"
        ),
    )
    parser.add_argument(
        "-f",
        "--fail-fast",
        action="store_true",
        help=(
            "stop running tests after first failure (this"
            " is a shorthand for -o FAIL_FAST, and is"
            " in addition to any other -o options)"
        ),
    )
    parser.add_argument("file", nargs="+", help="file containing the tests to run")

    if len(sys.argv[:]) == 0:
        parser.print_help()
        return
    args = parser.parse_args()

    return args


def flatten_test_suite(suite):
    # In hindsight this really isnt needed
    flatten = unittest.TestSuite()
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            flatten.addTests(flatten_test_suite(test))
        else:
            flatten.addTest(test)
    return flatten


def doctests(args):
    testfiles = args.file
    # Verbose used to be handled by the "inspect argv" magic in DocTestRunner,
    # but since we are using argparse we are passing it manually now.
    verbose = args.verbose
    options = 0
    for option in args.option:
        options |= doctest.OPTIONFLAGS_BY_NAME[option]
    if args.fail_fast:
        options |= doctest.FAIL_FAST

    doctest_suite = doctest.DocTestSuite(module="default_profile")
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    doctest_finder = doctest.DocTestFinder()
    found_test_cases = findTestCases("*")
    doctest.DocTestSuite("__main__", globs="*")

    for filename in testfiles:
        if filename.endswith(".py"):
            # It is a module -- insert its dir into sys.path and try to
            # import it. If it is part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            sys.path.insert(0, dirname)
            m = importlib.import_module(filename[:-3])
            del sys.path[0]
            failures, _ = testmod(m, verbose=verbose, optionflags=options)
        else:
            failures, _ = testfile(
                filename, module_relative=False, verbose=verbose, optionflags=options
            )


def add_test(testcase, suite=None):
    if suite is not None:
        suite = flatten_test_suite(suite)
    else:
        suite = unittest.TestCaseSuite()
    return suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(testcase))


def setup_test_logging():
    """Set up some logging so we can see what's happening."""
    logger = logging.getLogger(name=__name__)
    test_handler = logging.StreamHandler(stream=sys.stdout)
    test_formatter = logging.Formatter(
        fmt="%(created)f : %(module)s : %(levelname)s : %(message)s"
    )
    test_handler.setFormatter(test_formatter)
    test_handler.setLevel(logging.WARNING)
    logger.setLevel(logging.WARNING)
    logger.addHandler(test_handler)
    return logger


def run():

    args = _parse()
    if args is None:
        # hm what should i do
        return
    test_logger = setup_test_logging()
    # doctests()
    # Believe it or not this is in fact necessary if you want to run
    # the tests inside of IPython.
    old_sys_argv = sys.argv[:]
    sys.argv = get_ipython_cmd(as_string=False)
    test_00_ipython = importlib.import_module("test_00_ipython", package=".")
    test_20_aliases = importlib.import_module("test_20_aliases", package=".")

    if pytest is None:
        suite = TestSuite()
        all_test_suites = unittest.defaultTestLoader.discover(start_dir="test")
        # add_test(test_00_ipython.TestIPython(), suite)
        # add_test(test_20_aliases.TestAliases(), suite)
        tests = []

        for test in flatten_test_suite(all_test_suites):
            tests.append(test)
        suite.addTests(tests)
        successful = (
            unittest.TextTestRunner(verbosity=v, failfast=options.exitfirst)
            .run(suite)
            .wasSuccessful()
        )
        return 0 if successful else 1

    else:
        pytest.main()


if __name__ == "__main__":
    run()
