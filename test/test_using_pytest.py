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



def main():
    """Try a new unit testing framework.

    Erhm this is definitely not how you implement fixtures.

    """
    try:
        import pytest
    except (ImportError, ModuleNotFoundError):
        return

    # pytest.importorskip()
    @pytest.fixture
    def ip():
        return get_ipython()


if __name__ == "__main__":
    main()
