#!/usr/bin/env python3
import os
import shutil
import tempfile
import unittest

from os.path import abspath, realpath, isfile, exists

import pytest

from IPython.testing.globalipapp import get_ipython

from default_profile.startup.all_fault_handlers import tempdir, in_tempdir, in_dir


def remove_tmpdir(dir):
    try:
        shutil.rmtree(dir)
    except (NotADirectoryError, FileNotFoundError, OSError):
        pass
    except PermissionError:
        raise


@pytest.fixture
def cwd():
    return os.path.abspath(os.path.curdir)


class FixturesTest(unittest.TestCase):
    def setUp(self):
        # unittest's version of the tmpdir fixture
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(remove_tmpdir, self.tmpdir)

    # def test_rehashx_does_not_raise(self):
        # are you allowed to do this?
        # would something like this work
        # with self.assertRaises(None):
        # Wait this isn't a context manager??? hold the fuck up.
        # with not self.assertRaises(Exception):
            # get_ipython().run_line_magic('rehashx')


def test_tempdir():
    with tempdir() as tmpdir:
        fname = os.path.join(tmpdir, 'example_file.txt')
        with open(fname, 'wt') as fobj:
            fobj.write('a string\\n')
    assert not exists(tmpdir)


def test_in_tempdir(cwd):
    with in_tempdir() as tmpdir:
        with open('test.txt', 'wt') as f:
            f.write('some text')
        assert isfile('test.txt')
        assert isfile(os.path.join(tmpdir, 'test.txt'))
    assert not exists(tmpdir)


def test_given_directory(cwd):
    # Test InGivenDirectory
    with in_dir() as tmpdir:
        assert tmpdir==abspath(cwd)
    with in_dir(cwd) as tmpdir:
        assert tmpdir==cwd


if __name__ == "__main__":
    unittest.main()
