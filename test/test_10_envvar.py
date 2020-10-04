#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test environment related magics loaded on startup."""
# Yo please take note of the fact that the output from the 'outside setup_module'
# print statement appears first and i was not expecting that at all.
# inside of the setup_module the stderr and stdout are captured and saved
# for the report of pass/fails that comes up later.
# I'm assuming the first statement got run during collection or something.
from pathlib import Path
import platform
import unittest

import pytest

from default_profile.extensions.envvar import EnvironMagics


def setup_module():
    print('****** Inside setup_module ********\nWhat is the scope on this?\n')
    environ_magics = EnvironMagics()

    print(dir())


print('**************** Outside setup_module *********\n')
print(dir())


class TestPath(unittest.TestCase):
    """Need to do a few checks on pathlib before we start."""

    def test_backslashes(self):
        path = "C:\\Users\\fac\\Dropbox"
        foo = Path(path)
        self.assertIsInstance(Path(path), Path)


# def test__reader():
#     assert False
#

# def test__writer():
#     assert False


# def test__bufferedrw() -> object:
#     assert False


# def test_stdout():
#     assert False


if __name__ == "__main__":
    # pytest.mark.skip()
    pytest.main()
