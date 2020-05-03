#!/usr/bin/env python3
import shutil
import tempfile
import unittest

from IPython.testing.globalipapp import get_ipython


def remove_tmpdir(dir):
    try:
        shutil.rmtree(dir)
    except (NotADirectoryError, FileNotFoundError, OSError):
        pass
    except PermissionError:
        raise



class FixturesTest(unittest.TestCase):
    def setUp(self):
        # unittest's version of the tmpdir fixture
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(remove_tmpdir, self.tmpdir)

    def test_rehashx_does_not_raise(self):
        # are you allowed to do this?
        # would something like this work
        # with self.assertRaises(None):
        # Wait this isn't a context manager??? hold the fuck up.
        with not self.assertRaises(Exception):
            get_ipython().run_line_magic('rehashx')


if __name__ == "__main__":
    unittest.main()
