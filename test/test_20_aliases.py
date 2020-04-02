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
from contextlib import suppress
import importlib
import unittest
from unittest.case import TestCase

from IPython.core.getipython import get_ipython
from IPython.utils.capture import capture_output

try:
    import nose.tools as nt
    import nose
except (ImportError, ModuleNotFoundError):
    NO_NOSE = True
    from _pytest.outcomes import skip
    skip(allow_module_level=True)
else:
    NO_NOSE = None



with suppress(ImportError):
    from default_profile.startup import aliases_mod


def setup_module():
    if NO_NOSE:
        unittest.skip("No Nose")
    if get_ipython() is not None:
        return get_ipython().alias_manager
    else:
        unittest.skip("Not in IPython")



def test_alias_lifecycle(_ip):
    name = "test_alias1"
    cmd = 'echo "Hello"'
    am = setup_module()
    if am  is None:
        unittest.skip("How the fuck are these lines still executing.")
        return
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


# def test_alias_args_commented(_ip):
#     """Check that alias correctly ignores 'commented out' args"""
#     _ip.alias_manager.define_alias(
#         "alias", "commetarg echo this is %%s a commented out arg"
#     )

#     with capture_output() as cap:
#         _ip.run_cell("commetarg")

#     nt.assert_equal(cap.stdout, "this is %s a commented out arg")


def test_alias_args_commented_nargs(_ip):
    """Check that alias correctly counts args, excluding those commented out"""
    am = _ip.alias_manager
    alias_name = "comargcount"
    cmd = "echo this is %%s a commented out arg and this is not %s"

    am.define_alias(alias_name, cmd)
    assert am.is_alias(alias_name)

    thealias = am.get_alias(alias_name)
    nt.assert_equal(thealias.nargs, 1)


# TODO: well i suppose it should be obvious that you shouldn't do something like
# this because nobody wants interactive tests.
# @pytest.mark.xfail
# def test_that_hyphens_cant_be_aliases(_ip):
#     """This is a simple reminder that this won't behave as expected/desired."""
#     am = _ip.alias_manager
#     am.define_alias("fzf-tmux", "fzf-tmux -d 50")
#     _ip.run_line_magic("fzf-tmux", "")

if __name__ == '__main__':

    unittest.skipIf(NO_NOSE, 'Nose not installed.')
    # otherwise...
    unittest.main()
