
import importlib
import unittest
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

# Doesn't work. Says theres no bt_mod. Ugh
# bt_mod = importlib.import_module('default_profile.startup.33_bottom_toolbar')
# from bt_mod import BottomToolbar  # noqa
# maybe we should do
spec = importlib.util.spec_from_file_location(
    "../default_profile/startup/33_bottom_toolbar"
)
if spec is not None:
    bt_mod = importlib.util.module_from_spec(spec)
else:
    bt_mod = importlib.import_module("default_profile.startup.33_bottom_toolbar")

if bt_mod is None:
    unittest.skip("Import failure for bottom_toolbar.")

if bt_mod.get_app() is None:
    unittest.skip("Prompt toolkit not running.")


class TestBottomToolbar(TestCase):
    def setUp(self, _ip):
        """Is this supposed to be called something different?"""
        self.toolbar = bt_mod.BottomToolbar(bt_mod.get_app())
        if bt_mod.BottomToolbar() is None:
            self.toolbar = _ip
        if _ip is not None:
            bt_mod.add_toolbar(self.toolbar)

    def test_toolbar_existence(self):
        self.assertIsNotNone(self.toolbar)

    def test_toolbar_gets_to_stdout(self):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            print(self.toolbar)

        self.assertIsInstance(fake_out.getvalue(), str)
