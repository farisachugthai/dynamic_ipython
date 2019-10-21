#!/usr/bin/env python3
"""Arguably the best canary in the coal mine that something's wrong with setup.
"""
import logging
import unittest

import IPython
from IPython import get_ipython


class TestIPython(unittest.TestCase):
    """For debugging the test suite.

    Who knew overriding the :class:`unittest.TestCase()` ``__init__`` method would be
    such a hassle?
    """

    shell = get_ipython()

    def __init__(self, shell=None):
        super().__init__()
        if shell is not None:
            self.shell = shell
        else:
            from IPython import start_ipython
            self.shell = start_ipython()

    def test_ipython(self):
        """Produces unexpected results. TODO."""
        # print(type(self.shell))
        # self.assertIsInstance(self.shell, IPython.core.interactiveshell.InteractiveShell)
        self.assertIsInstance(self.shell, str)

    def runTest(self):
        """runTest function for:

        :mod:`test_00_ipython`
        :class:`TestIPython()`
        :func:`runTest`

        As a result, the only use of this function will be to call the necessary
        methods.
        """
        return self.test_ipython()


if __name__ == "__main__":
    unittest.main()
