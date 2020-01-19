import doctest
import importlib
import sys
import unittest
from unittest.suite import TestSuite
from unittest.case import TestCase

from IPython.testing.tools import get_ipython_cmd


def _test():
    import argparse

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
    args = parser.parse_args()
    testfiles = args.file
    # Verbose used to be handled by the "inspect argv" magic in DocTestRunner,
    # but since we are using argparse we are passing it manually now.
    verbose = args.verbose
    options = 0
    for option in args.option:
        options |= doctest.OPTIONFLAGS_BY_NAME[option]
    if args.fail_fast:
        options |= doctest.FAIL_FAST
    for filename in testfiles:
        if filename.endswith(".py"):
            # It is a module -- insert its dir into sys.path and try to
            # import it. If it is part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            sys.path.insert(0, dirname)
            m = __import__(filename[:-3])
            del sys.path[0]
            failures, _ = testmod(m, verbose=verbose, optionflags=options)
        else:
            failures, _ = testfile(
                filename, module_relative=False, verbose=verbose, optionflags=options
            )
        if failures:
            return 1
    return 0


if __name__ == "__main__":
    # Believe it or not this is in fact necessary
    old_sys_argv = sys.argv[:]
    # DONT FORGET SPACES
    # sys.argv = [sys.executable, ' -m', ' unittest', ' -v']
    sys.argv = get_ipython_cmd(as_string=False)
    # todo: add options
    test_00_ipython = importlib.import_module("test_00_ipython", package=".")
    test_20_aliases = importlib.import_module("test_20_aliases", package=".")

    suite = TestSuite()
    suite.addTest(test_00_ipython.TestIPython())
    suite.addTest(test_20_aliases.TestAliases())
    unittest.main()

    _test()
    # sys.argv = old_sys_argv
