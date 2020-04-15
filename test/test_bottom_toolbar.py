#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import inspect
import sys
import unittest
from io import StringIO
from importlib.util import module_from_spec
from unittest import TestCase
from unittest.mock import patch

from IPython.testing.globalipapp import get_ipython
from IPython.terminal.interactiveshell import InteractiveShell

try:
    spec = importlib.util.spec_from_file_location(
        "default_profile.startup.bottom_toolbar_mod",
        location="../default_profile/startup/bottom_toolbar",
    )
except ModuleNotFoundError:
    spec = None

if spec is not None:
    bt_mod = module_from_spec(spec)
else:
    bt_mod = importlib.import_module("default_profile.startup.bottom_toolbar")

if bt_mod is None:
    unittest.skip("Import failure for bottom_toolbar.")


def debugging_myoutput(capsys):
    # or use "capfd" for fd-level
    print()
    sys.stderr.write("world\n")
    captured = capsys.readouterr()
    # todo
    assert captured


@unittest.skipIf(bt_mod.get_app() is None, "prompt_toolkit not running")
class TestBottomToolbar(TestCase):
    # ugh this is proving entirely too difficult

    @classmethod
    def setUpClass(cls):
        cls.logpoint()
        _ip = get_ipython()
        if bt_mod.BottomToolbar() is None:
            if _ip is not None:
                bt_mod.add_toolbar(cls.toolbar)

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

