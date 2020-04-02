#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from importlib import import_module
import inspect
from inspect import getdoc
import logging
import pydoc
import sys

import IPython
from IPython.core.getipython import get_ipython
from IPython.core.error import UsageError
from IPython.core.magic import line_magic, magics_class, Magics
from IPython.core.magics.namespace import NamespaceMagics
from IPython.core.page import pager_page


class NotInIPythonError(RuntimeError):
    """Error raised when a magic is invoked outside of IPython."""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args)


@magics_class
class PyPager(Magics):
    """A pager if you're outside of IPython."""

    def __init__(self, use_pager=True, **kwargs):
        """Initializes the class.

        This occurs by binding an optional text to the instance and determining
        whether to use a pager or output by printing to the shell.

        Parameters
        ----------
        text : str, optional
            Text to page
        use_pager : bool, optional
            Whether to print to the shell or pipe to a pager.
        """
        super().__init__(**kwargs)
        self.use_pager = use_pager
        # self.call(*args)

    def __repr__(self):
        return "".join(self.__class__.__name__)

    def __str__(self):
        return "A pager for files you'd like to inspect. Or interactive variables."

    def __call__(self, text=None):
        return pydoc.tempfilepager(text, self.use_pager)

    def call(self, text):
        return self.__call__(text)


def blocking_pager(text):
    """A pipe pager that works on Windows. Doesn't colorize anything.

    It's better that way though as we can send the contents elsewhere to
    be highlighted.

    Better to keep things separated.
    """
    with open(text, "rt") as f:
        pydoc.pipepager(f.read(), "less -JRKMLige ")


def get_docs_and_page():
    """Resourceful way to parse sys.argv and then expand a ``*args``."""
    _, *args = sys.argv[:]
    if len(args) > 0:
        print(getdoc(*args))
        return getdoc(*args)


def were_in_ipython():
    """Call ipython to make sure we're really in it."""
    shell = get_ipython()
    if shell is None:
        raise NotInIPythonError
    else:
        return True


def provided_or_last(s=None, shell=None):
    """Either run a provided code_cell from a user or rerun their last input.

    Parameters
    ----------
    s : str, optional
        str to page
    shell : IPython instance, optional

    Returns
    --------
    code_to_page :
        Found user code.

    Notes
    -------
    We should consider using something else to find user code.

    """
    if shell is None:
        shell = get_ipython()
    if shell is None:
        return
    if s is not None:
        code_to_page = shell.find_user_code(s, skip_encoding_cookie=True)
    else:
        # noinspection PyProtectedMember
        code_to_page = shell._i

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
    if hasattr(namespace, "pycat"):
        try:
            get_ipython().run_line_magic("pycat", "code")
        except (KeyboardInterrupt, EOFError):
            return
    else:
        raise UsageError("ya dun goofed")


if __name__ == "__main__":
    get_ipython().register_magic_function(c)
    # inspector = IPython.core.oinspect.Inspector()
