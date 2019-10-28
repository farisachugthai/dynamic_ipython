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
import logging
import pydoc

import IPython
from IPython import get_ipython
from IPython.core.magic import line_magic
# from IPython.core.magics import
# Might need some of the funcs from IPython.utils.{PyColorize,coloransi,colorable}


@line_magic
def p(shell=None, s=None):
    """Intentionally abbreviated function call to `%pycat`."""
    if shell is None:
        shell = get_ipython()
    if s is None:
        IPython.core.page.page(shell.pycolorize(_i))
    else:
        IPython.core.page.page(shell.pycolorize(shell.find_user_code(s, skip_encoding_cookie=True)))


if __name__ == "__main__":
    get_ipython().register_magic_function(p)
