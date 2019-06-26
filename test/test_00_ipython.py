#!/usr/bin/env python3
"""Arguably the best canary in the coal mine that something's wrong with setup."""
import unittest

import IPython
from IPython import get_ipython


class TestIPython(unittest.TestCase):
    """For debugging the test suite."""

    shell = get_ipython()

    def __init__(self, shell):
        self.shell = shell
        super().__init__()

    def test_ipython(self):
        self.assertIsInstance(self.shell, IPython.core.interactiveshell.InteractiveShell)


if __name__ == "__main__":
    unittest.main()
