#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import unittest
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from IPython.terminal.interactiveshell import InteractiveShell
from py._path.local import LocalPath

import default_profile

_bt_mod = LocalPath('../default_profile/startup/33_bottom_toolbar.py')
bt_mod = _bt_mod.pyimport()


if bt_mod.get_app() is None:
    unittest.skip("Prompt toolkit not running.")


def shell():
    return InteractiveShell()


def pt_app():
    return shell.pt_app


@unittest.skipIf(bt_mod.get_app() is None, "prompt_toolkit not running")
class TestBottomToolbar(TestCase):
    def setUp(self):
        """Is this supposed to be called something different?"""
        if bt_mod.BottomToolbar() is None:
            if _ip is not None:
                bt_mod.add_toolbar(self.toolbar)

    def test_toolbar_existence(self, _ip):
        self.toolbar = bt_mod.BottomToolbar(_ip.pt_app)
        self.assertIsNotNone(self.toolbar)

    def test_toolbar_gets_to_stdout(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            print(self.toolbar)

        self.assertIsInstance(fake_out.getvalue(), str)
