#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rewrite the module that creates the ``%pycat`` magic.

In it's current implementation, the pager gives Windows a dumb terminal and
never checks for whether :command:`less` is on the :envvar:`PATH` or
if the user has a pager they wanna implement!

Working Implementation
----------------------

Oct 28, 2019:

Just ran this in the shell and I'm really pleased with it.

It utilizes the :attr:`autocall` functionality of IPython, works with the
pycolorize utils, uses the page.page core function.

If the user doesn't provide an argument, then just show them the last input
they gave us especially since that var is **guaranteed** to always
be there.

Like solid shit man. And I came up with this in 10 minutes too!

.. testsetup::

    import IPython
    from IPython import get_ipython
    from IPython.core.magic import line_magic

.. ipython::

    In [105]: @line_magic
        ...: def p(shell=None, s=None):
        ...:     if shell is None:
        ...:         shell = get_ipython()
        ...:     if s is None:
        ...:         IPython.core.page.page(shell.pycolorize(_i))
        ...:     else:
        ...:         IPython.core.page.page(shell.pycolorize(shell.find_user_code(s, skip_encoding_cookie=True)))

    In [106]: /p
    @line_magic
    def p(shell=None, s=None):
        if shell is None:
            shell = get_ipython()
        if s is None:
            IPython.core.page.page(shell.pycolorize(_i))
        else:
            IPython.core.page.page(shell.pycolorize(shell.find_user_code(s, skip_encoding_cookie=True)))


.. todo:: Literally how is this the part that's giving me errors.

::

    PAGER_LOGGER = logging.getLogger(name='default_profile.util').getchild('pager2')
    PAGER_HANDLER = logging.StreamHandler()
    PAGER_LOGGER.addHandler(PAGER_HANDLER)


"""
from importlib import import_module
import inspect
import logging
import pydoc
import sys

import IPython
from IPython import get_ipython
from IPython.core.error import UsageError
from IPython.core.magic import line_magic
from IPython.core.magics.namespace import NamespaceMagics
from IPython.core.page import pager_page
# from IPython.core.magics import
# Might need some of the funcs from IPython.utils.{PyColorize,coloransi,colorable}


class NotInIPythonError(RuntimeError):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


def were_in_ipython():
    """Call ipython to make sure we're really in it."""
    shell = get_ipython()
    if shell is None:
        raise NotInIPythonError
    # ('Not in IPython.')


def provided_or_last(s=None):
    """Either run a provided code_cell from a user or rerun their last input."""
    if s is not None:
        code_to_page = find_user_code(s, skip_encoding_cookie=True)
    else:
        code_to_page = _i

    return code_to_page


@line_magic
def c(s=None):
    """Intentionally abbreviated function call to `%pycat`.

    This implementation has the added benefit of wrapping everything in a
    try/except that catches KeyboardInterrupts and EOFErrors because pycat
    doesn't.

    Parameters
    ----------
    s : str
        String to page.

    """
    if not were_in_ipython():
        return
    code = provided_or_last(s)
    namespace = NamespaceMagics()
    if hasattr(namespace, 'pycat'):
        try:
            get_ipython().run_line_magic('pycat', 'code')
        except (KeyboardInterrupt, EOFError):
            return
    else:
        raise UsageError('ya dun goofed')


if __name__ == "__main__":
    get_ipython().register_magic_function(c)
    if len(sys.argv[:]) > 1:
        c(sys.argv[1:])
