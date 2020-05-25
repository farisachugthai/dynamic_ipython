#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a single entry point for the test suite."""
import argparse
import doctest
import importlib
import logging
import multiprocessing
import os
import sys
import unittest
import warnings

from doctest import testmod, testfile
from types import ModuleType

# from unittest.loader import TestLoader, defaultTestLoader
# from unittest.loader import  findTestCases  # fuck why is this coming up as unresolved
from unittest.runner import TextTestRunner
from unittest.suite import TestSuite

# don't forget about this as it may come in handy
# from IPython.lib.deepreload import reload
from IPython.testing.tools import get_ipython_cmd

try:
    import nose  # noqa F401
except ImportError as e:
    print(e)

try:
    import pytest
except ImportError:
    warnings.warn("No Pytest. Using unittest.")
    pytest = None

from default_profile import __version__


# Global:
logging.captureWarnings(True)


def _parse():
    """Use argparse to get user arguments."""
    parser = argparse.ArgumentParser(description="Unittest/doctest runner.")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbosity",
        default=False,
        help="print very verbose output for all tests",
    )

    parser.add_argument(
        "-ll",
        "--log_level",
        dest="log_level",
        metavar="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
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
        "-m", "--module", type=ModuleType, nargs="+", help=("Module to run")
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
    parser.add_argument(
        "-c",
        "--file",
        nargs="+",
        type=argparse.FileType("r"),
        help="file containing the tests to run",
    )

    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s" + __version__
    )

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


def generate_doctest_suite():
    """Default doctest_suite to generate. Can be overridden on the command line."""
    return doctest.DocTestSuite(module="default_profile", globs="*")


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

    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # where were these used?
    # doctest_finder = doctest.DocTestFinder()
    # found_test_cases = findTestCases("*")
    # doctest.DocTestSuite("__main__", globs="*")

    for filename in testfiles:
        if filename.endswith(".py"):
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
        suite = unittest.TestSuite()
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


# Here's the unittest alternative to pytest.importorskip
def import_module(name, *, required_on=None):
    """Import and return the module to be tested.

    :raises SkipTest: When not installed

    If 'deprecated' is True, any module or package deprecation messages
    will be suppressed.

    If a module is 'required_on' a platform but optional for
    others, set 'required_on' to an iterable of platform prefixes which will be
    compared against `sys.platform`.
    """
    with warnings.catch_warnings():
        try:
            return importlib.import_module(name)
        except ImportError as msg:
            if sys.platform.startswith(tuple(required_on)):
                raise
            raise unittest.SkipTest(str(msg))


def run():
    # Believe it or not this is in fact necessary if you want to run
    # the tests inside of IPython.
    _ = sys.argv[:]
    sys.argv = get_ipython_cmd(as_string=False)
    args = _parse()
    if args is None:
        # hm what should i do
        return

    try:
        log_level = args.log_level
    except AttributeError:  # IndexError?
        test_logger = setup_test_logging()
    else:
        logging.basicConfig(level=log_level)

    try:
        v = args.verbosity
    except AttributeError:
        v = False

    try:
        option = args.option
    except AttributeError:
        option = False

    # doctests()
    # test_00_ipython = importlib.import_module("test_00_ipython", package=".")
    # test_20_aliases = importlib.import_module("test_20_aliases", package=".")

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
            TextTestRunner(verbosity=v, failfast=option.exitfirst)
            .run(suite)
            .wasSuccessful()
        )
        return 0 if successful else 1

    else:
        # TODO: args can be be passed to this so add args for pytest in that parse func above
        pytest.main(plugins=[])


if __name__ == "__main__":
    mp_logger = multiprocessing.get_logger()
    mp_context = multiprocessing.get_context()
    mp_logger.setLevel(logging.INFO)
    mp_handler = logging.StreamHandler()
    mp_handler.setLevel(logging.INFO)
    mp_logger.handlers = []
    mp_logger.addHandler(mp_handler)
    mp_logger.info(f"mp context: {mp_context}")

    run()
