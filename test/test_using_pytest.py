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

from IPython.core.get import get_ipython


COLORS = {
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "bold": "\x1b[1m",
    "reset": "\x1b[0m",
}
RE_COLORS = {k: re.escape(v) for k, v in COLORS.items()}


class Option:
    def __init__(self, verbosity=0):
        self.verbosity = verbosity

    @property
    def args(self):
        values = []
        values.append("--verbosity=%d" % self.verbosity)
        return values


@pytest.fixture(
    params=[Option(verbosity=0), Option(verbosity=1), Option(verbosity=-1)],
    ids=["default", "verbose", "quiet"],
)
def option(request):
    return request.param
