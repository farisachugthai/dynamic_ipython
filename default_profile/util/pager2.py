#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import contextlib
import io
import logging
import pydoc
import shlex
import sys
from inspect import getdoc

from IPython.core.getipython import get_ipython
from IPython.core.magic import line_magic, magics_class, Magics
from IPython.core.magics.namespace import NamespaceMagics
from IPython.terminal.interactiveshell import TerminalInteractiveShell

from default_profile.ipython_config import NotInIPythonError, UsageError
from default_profile.startup.documenters import HelpMagics

logging.basicConfig()


def _bool_globals_check(index):
    return any([item for item in globals().keys() if item == index])


def _ofind(obj):
    # IPythons _ofind doesnt find things in globals ffs
    if _bool_globals_check(obj):
        return obj
    return TerminalInteractiveShell()._ofind(obj)


def _bool_globals_locals_check(index):
    return any(*[
        [item for item in globals().keys() if item == index],
        [item for item in locals().keys() if item == index],
    ])


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


@magics_class
class PagerMagics(Magics):
    """A pager if you're outside of IPython."""

    shell = get_ipython()

    def __init__(self, use_pager=True, cmd=None, **kwargs):
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
        super().__init__(self.shell, **kwargs)
        self.use_pager = use_pager
        # self.call(*args)
        self.cmd = "less -JRKMLige " if cmd is None else cmd

    def __repr__(self):
        return "".join(self.__class__.__name__)

    def __str__(self):
        return "A pager for files you'd like to inspect. Or interactive variables."

    def blocking_pager(self, text, cmd=None):
        """A pipe pager that works on Windows. Doesn't colorize anything.

        It's better that way though as we can send the contents elsewhere to
        be highlighted.

        Better to keep things separated.
        """
        return pydoc.tempfilepager(text, self.use_pager)

    def factory(self, text=None, func=None, cmd=None, *args, **kwargs):
        if text is None:
            if args:
                text = args
            else:
                raise UsageError
        if hasattr(text, "strip"):
            text = pydoc.getdoc(text.strip())

        cmd = shlex.quote(cmd) if cmd is not None else self.cmd
        func = func if func is not None else pydoc.pipepager
        with contextlib.redirect_stderr(sys.stderr):
            func(text, cmd)

    @line_magic
    def c(self, s=None):
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
        code = provided_or_last(s)
        self.shell.run_line_magic("pycat", s)

    @line_magic
    def page(self, s):
        """Pretty print the object and display it through a pager.

        If no object is given, use _ (last output).::

            %page [options] OBJECT


        Options
        -------
        .. option:: -r
            page str(object), don't pretty-print it.

        .. option:: -o
            Print to console using bat.

        """
        s = str(s)
        if _bool_globals_check(s):
            txt = inspect.getdoc(s.__class__)
            logging.warning('First')
            self.blocking_pager(txt)
            return

        # After a function contributed by Olivier Aubert, slightly modified.

        # Process options/args
        opts, args = self.parse_options(s, 'r')
        raw = 'r' in opts
        if args == '':
            raise UsageError("Can't find documentation of None")

        oname = args and args or '_'
        info = self.shell._ofind(oname)
        if info['found']:
            txt = (raw and str or pformat)(info['obj'])
            if 'o' in opts:
                logging.warning('Second')
                self.blocking_pager(txt, cmd='bat --page never ')
                return
            logging.warning('Third')
            self.blocking_pager(txt)
        else:
            logging.warning('Object `%s` not found' % oname)


if __name__ == "__main__":
    # made it a method but as a syntax reminder
    # get_ipython().register_magic_function(c)
    get_ipython().register_magics(PagerMagics())

    # inspector = IPython.core.oinspect.Inspector()
