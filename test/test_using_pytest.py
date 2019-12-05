#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilize pytest.

:date: Sep 23, 2019

Came across an interesting function today.

.. func:: pytest.importorskip

    pytest.importorskip = importorskip(modname: str, minversion: Union[str, NoneType] = None, reason: Union[str, NoneType] = None) -> Any
    Imports and returns the requested module ``modname``, or skip the
    current test if the module cannot be imported.

    :param str modname: the name of the module to import
    :param str minversion: if given, the imported module's ``__version__``
        attribute must be at least this minimal version, otherwise the test is
        still skipped.
    :param str reason: if given, this reason is shown as the message when the
        module cannot be imported.
    :returns: The imported module. This should be assigned to its canonical
        name.

Example::

    docutils = pytest.importorskip("docutils")

That's pretty neat! I feel like I was trying to set something like that up
with the sphinx build so it's cool to see it in this context.

"""
import sys
import warnings

from IPython import get_ipython


def run_pytest():
    """Make sure pytest is installed before running."""
    try:
        import pytest  # noqa F401
    except ImportError as e:
        warnings.warn(e)
        pytest = None
    if pytest is not None:
        pytest.main()


if __name__ == "__main__":
    run_pytest()
