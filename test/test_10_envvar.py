#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test environment related magics loaded on startup."""

from pathlib import Path
import platform
import unittest

import pytest

from default_profile.startup import envvar_mod


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


if __name__ == '__main__':
    pytest.mark.skip()
