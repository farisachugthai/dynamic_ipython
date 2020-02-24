#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test environment related magics loaded on startup."""

from pathlib import Path
import platform
import unittest
from default_profile.startup import envvar_mod


class TestPath(unittest.TestCase):
    """Need to do a few checks on pathlib before we start."""

    # def test_backslashes(self):
    # Wow this causes an error even with assertRaises
    # with self.assertRaises(SyntaxError):
    #     path = "C:\Users\fac\Dropbox"
    #     foo = Path(path)
    # self.assertIsInstance(Path(path), Path)

    def test_backslashes(self):
        path = "C:\\Users\\fac\\Dropbox"
        foo = Path(path)
        self.assertIsInstance(Path(path), Path)

    @unittest.skipUnless(
        platform.platform().startswith("Win"),
        "Windows Only. Checks for existence of non-existnt folder on Unix",
    )
    def test_whitespace(self):
        r"""Erhm.

        ::

            self = <dynamic_ipython.test.test_10_envvar.TestPath testMethod=test_whitespace>

                @unittest.skipUnless(
                    platform.platform().startswith("Win"),
                    "Windows Only. Checks for existence of non-existnt folder on Unix",
                )
                def test_whitespace(self):
                    # How weird is the backslash handling here?
                    with self.assertWarns(DeprecationWarning):  # and why deprecation?
                        path = "C:\Program Files"
                        pathlibed = Path(path)
                        self.assertIsInstance(pathlibed, Path)
            >           self.assertTrue(pathlibed.exists())
            E           AssertionError: DeprecationWarning not triggered

            test\test_10_envvar.py:36: AssertionError

            C:\Users\fac\projects\dynamic_ipython\test\test_10_envvar.py:33:
            DeprecationWarning: invalid escape sequence \P
            path = "C:\Program Files"

        """
        # How weird is the backslash handling here?
        # with self.assertWarns(DeprecationWarning):  # and why deprecation?
        path = "C:\Program Files"
        pathlibed = Path(path)
        self.assertIsInstance(pathlibed, Path)
        self.assertTrue(pathlibed.exists())

    def test_unc_path(self):
        path = "\\C"
        # TODO

    def test_invalid_path(self):
        path = "C:\not\a\\path"
        with self.assertRaises(OSError):
            foo = Path(path).exists()


class TestEnvironMagics(unittest.TestCase):
    pass
