import importlib
import pytest

# Doesn't work. Says theres no bt_mod. Ugh
# bt_mod = importlib.import_module('default_profile.startup.33_bottom_toolbar')
# from bt_mod import BottomToolbar  # noqa
# maybe we should do
# importlib.util.spec_from_file_location
# importlib.util.mod_from_spec then proceed?

# def test_bottom_toolbar_exists():
#     assert BottomToolbar()
