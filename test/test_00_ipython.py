#!/usr/bin/env python3
"""Arguably the best canary in the coal mine that something's wrong with setup.

Jul 08, 2019:

Today we learned something!

If you create a class that inherits from :class:`unittest.TestCase()`, it may
be useful to check out these lines from the official lib.

.. code-block:: rst

    A class whose instances are single test cases.

    **By default, the test code itself should be placed in a method named
    'runTest'.**

    If the fixture may be used for many test cases, create as
    many test methods as are needed. When instantiating such a TestCase
    subclass, specify in the constructor arguments the name of the test method
    that the instance is to execute.

    Test authors should subclass TestCase for their own tests. Construction
    and deconstruction of the test's environment ('fixture') can be
    implemented by overriding the 'setUp' and 'tearDown' methods respectively.

    If it is necessary to override the ``__init__`` method, the base class
    __init__ method must always be called. It is important that subclasses
    should not change the signature of their __init__ method, since instances
    of the classes are instantiated automatically by parts of the framework
    in order to be run.

    When subclassing TestCase, you can set these attributes:
    * failureException: determines which exception will be raised when
        the instance's assertion methods fail; test methods raising this
        exception will be deemed to have 'failed' rather than 'errored'.
    * longMessage: determines whether long messages (including repr of
        objects used in assert methods) will be printed on failure in *addition*
        to any explicit message passed.
    * maxDiff: sets the maximum length of a diff in failure messages
        by assert methods using difflib. It is looked up as an instance
        attribute so can be configured by individual tests if required.

That's the ``__doc__`` for :class.`unittest.case.TestCase()`.

"""
import logging
import unittest

import IPython
from IPython import get_ipython


logging.basicConfig(level=logging.INFO)


class TestIPython(unittest.TestCase):
    """For debugging the test suite."""

    def __init__(self, shell=None):
        """Initialize IPython for unit testing."""
        super().__init__()
        if shell is not None:
            self.shell = shell
        else:
            self.shell = get_ipython()

    def test_ipython(self):
        """Test that the object returns an IPython instance.

        Mostly here to check that I'm using :mod:`unittest` correctly.
        """
        logging.info('Type of self.shell is: {}'.format(type(self.shell)))
        self.assertIsInstance(self.shell, IPython.core.interactiveshell.InteractiveShell)

    def runTest(self):
        """This is required as stated in the unittest.TestCase docstring.

        Begin runTest
        =============

        """
        return self.test_ipython()


if __name__ == "__main__":
    unittest.main()
