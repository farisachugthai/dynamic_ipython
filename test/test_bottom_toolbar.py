#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import inspect
import unittest
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from IPython.terminal.interactiveshell import InteractiveShell

spec = importlib.util.spec_from_file_location(
    "../default_profile/startup/33_bottom_toolbar"
)
if spec is not None:
    bt_mod = importlib.util.module_from_spec(spec)
else:
    bt_mod = importlib.import_module("default_profile.startup.33_bottom_toolbar")

if bt_mod is None:
    unittest.skip("Import failure for bottom_toolbar.")


def shell():
    return InteractiveShell()


def pt_app():
    return shell.pt_app


@unittest.skipIf(bt_mod.get_app() is None, "prompt_toolkit not running")
class TestBottomToolbar(TestCase):
    # ugh this is proving entirely too difficult

    def setUp(self):
        """Is this supposed to be called something different?"""
        self.logpoint()
        if bt_mod.BottomToolbar() is None:
            if _ip is not None:
                bt_mod.add_toolbar(self.toolbar)

    def test_toolbar_existence(self, _ip):
        self.logpoint()
        self.toolbar = bt_mod.BottomToolbar(_ip.pt_app)
        self.assertIsNotNone(self.toolbar)

    def test_toolbar_gets_to_stdout(self):
        self.logpoint()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            print(self.toolbar)

        self.assertIsInstance(fake_out.getvalue(), str)

    def logpoint(self):
        currentTest = self.id().split(".")[-1]
        callingFunction = inspect.stack()[1][3]
        print("in %s - %s()" % (currentTest, callingFunction))
