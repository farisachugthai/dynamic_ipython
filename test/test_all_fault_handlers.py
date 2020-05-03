#!/usr/bin/env python3
import unittest

from IPython.testing.globalipapp import get_ipython


class FixturesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(remove_tmpdir, self.tmpdir)


if __name__ == "__main__":
    unittest.main()
