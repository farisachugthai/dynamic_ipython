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


Original Pydoc Implementation and Errors
----------------------------------------

$ pydoc FRAMEOBJECTS
Traceback (most recent call last):
  File "C:/tools/miniconda3/lib/runpy.py", line 193, in _run_module_as_main
    "__main__", mod_spec)
  File "C:/tools/miniconda3/lib/runpy.py", line 85, in _run_code
    exec(code, run_globals)
    elif request in self.topics: self.showtopic(request)
  File "C:/tools/miniconda3/lib/pydoc.py", line 2021, in showtopic
    return self.showtopic(target, more_xrefs)
  File "C:/tools/miniconda3/lib/pydoc.py", line 2037, in showtopic
    pager(doc)
  File "C:/tools/miniconda3/lib/pydoc.py", line 1449, in pager
    pager(text)
  File "C:/tools/miniconda3/lib/pydoc.py", line 1462, in <lambda>
    return lambda text: tempfilepager(plain(text), use_pager)
  File "C:/tools/miniconda3/lib/pydoc.py", line 1519, in tempfilepager
    os.system(cmd + ' "' + filename + '"')
KeyboardInterrupt


Outside of the stupid traceback, that command worked perfectly for me.

I have $PAGER set on Windows {which I realize isn't typical}, however we should
re-use this implementation entirely and cut IPython.core.page.page out.


In [63]: pydoc.pipepager(inspect.getdoc(arg), os.environ.get('PAGER'))

Despite the source code of the std lib stating that pipes are completely broken on windows,
this worked just fine for me.

Define arg as an object like if you pass a string it'll give you the help message
for a str.

:mod:`inspect` has a million more methods and pydoc does too so possibly change the
:func:`inspect.getdoc` part, but honestly that one line is 80% of the way
to what I've been trying to do.

Nov 17, 2019:

Yo this is outrageous how inconsistently ANYTHING is working for me.


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
    """Error raised when a magic is invoked outside of IPython."""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class PyPager:
    """A pager if you're outside of IPython."""

    def __init__(self, *args):
        self.call(*args)

    def __repr__(self):
        return ''.join(self.__class__.__name__)

    def __str__(self):
        return "A pager for files you'd like to inspect. Or interactive variables."

    def __call__(self, text, use_pager=True):
        return pydoc.tempfilepager(text, use_pager)

    def call(self, text, use_pager=True):
        return self.__call__(text, use_pager=use_pager)


def blocking_pager(text):
    """A pipe pager that works on Windows. Doesn't colorize anything.

    It's better that way though as we can send the contents elsewhere to
    be highlighted.

    Better to keep things separated.
    """
    with open(text, 'rt') as f:
        pydoc.pipepager(f.read(), 'less -JRKMLige ')


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

    .. note:: The internal variable namespace, or an instance of the magic
              :class:`~IPython.core.magics.namespace.NameSpaceMagics`
              can display the magics through the attribute ...magics.

    Parameters
    ----------
    s : str
        String to page.

    """
    if not were_in_ipython():
        PyPager(*sys.argv[1:])
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
