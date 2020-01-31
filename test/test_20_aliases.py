# -*- coding: utf-8 -*-
"""Test that the :class:`IPython.core.AliasManager` behaves as expected.

Took this from the :mod:`IPython` team insofar.

Should definitely consider rewriting it.
But like partially because plagariasm, partially
because wth is this saying?

.. tip:: pytest

    If you pass an argument to your functions and invoke pytest,
    it will assume that the passed argument is a fixture you're feeding
    to it. Interesting.

"""
import unittest
from unittest.case import TestCase

from IPython.utils.capture import capture_output

try:
    import nose.tools as nt
    import nose
except (ImportError, ModuleNotFoundError):
    NO_NOSE = True
else:
    NO_NOSE = None

from default_profile.startup import aliases_mod
import pytest


def test_alias_lifecycle(_ip):
    name = "test_alias1"
    cmd = 'echo "Hello"'
    am = _ip.alias_manager
    am.clear_aliases()
    am.define_alias(name, cmd)
    assert am.is_alias(name)
    nt.assert_equal(am.retrieve_alias(name), cmd)
    nt.assert_in((name, cmd), am.aliases)

    # Test running the alias
    orig_system = _ip.system
    result = []
    _ip.system = result.append
    try:
        _ip.run_cell("%{}".format(name))
        result = [c.strip() for c in result]
        nt.assert_equal(result, [cmd])
    finally:
        _ip.system = orig_system

    # Test removing the alias
    am.undefine_alias(name)
    assert not am.is_alias(name)
    with nt.assert_raises(ValueError):
        am.retrieve_alias(name)
    nt.assert_not_in((name, cmd), am.aliases)


def test_alias_args_error(_ip):
    """Error expanding with wrong number of arguments."""
    _ip.alias_manager.define_alias("parts", "echo first %s second %s")
    # capture stderr:
    with capture_output() as cap:
        _ip.run_cell("parts 1")

    nt.assert_equal(cap.stderr.split(":")[0], "UsageError")


def test_alias_args_commented(_ip):
    """Check that alias correctly ignores 'commented out' args"""
    _ip.alias_manager.define_alias("alias", "commetarg echo this is %%s a commented out arg")

    with capture_output() as cap:
        _ip.run_cell("commetarg")

    nt.assert_equal(cap.stdout, "this is %s a commented out arg")


def test_alias_args_commented_nargs(_ip):
    """Check that alias correctly counts args, excluding those commented out"""
    am = _ip.alias_manager
    alias_name = "comargcount"
    cmd = "echo this is %%s a commented out arg and this is not %s"

    am.define_alias(alias_name, cmd)
    assert am.is_alias(alias_name)

    thealias = am.get_alias(alias_name)
    nt.assert_equal(thealias.nargs, 1)


if __name__ == "__main__":
    pytest.main()