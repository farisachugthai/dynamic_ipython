#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export functions to redirect :func:`help` output.

This module utilizes the examples given in the official documentation
for :mod:`contextlib`.

In addition to utilizing :mod:`contextlib`, we create a function that allows
that allows searching through the members of an object.

This is intended to be exposed to the user as a quick, interactive tool
with an easier "grep-like" interface for objects that are too large
to be quickly and easily understood based on the output of :func:`dir`.

.. todo:: :mod:`pydoc` actually has a giant API so we could also use that.

"""
import contextlib
import io
import logging
import pydoc
import re
import sys

# noinspection PyProtectedMember
from pydoc import Helper
# from pydoc_data.topics import topics  # idk if this is official API but i like it
from traceback import print_exc
from typing import Callable

from IPython.core.getipython import get_ipython
from IPython.core.magic import Magics, magics_class, register_line_magic, line_magic
from IPython.utils.text import SList

import pygments
from pygments.lexers.python import PythonLexer, PythonTracebackLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

from default_profile.ipython_config import UsageError


class HelpHelper(Helper):

    def help(self, request):
        pass  # todo

@magics_class
class HelpMagics(Magics):
    """Useful magics for when you're introspecting things.

    Similar to a few of the existing namespace magics.

    .. todo::
        args = self.parse_args()
        I feel like that should be in the base Magics class's ``__call__``
        method. Or something that we don't have to manually call it every
        single time we need it.

    """

    # todo
    helper = HelpHelper()
    keywords = helper.keywords
    topics = helper.topics

    @line_magic
    def print_help(self, arg=None):
        """Redirect :func:`help` to ``sys.stderr``.

        Parameters
        ----------
        arg : obj, optional
            Object to run :magic:`pinfo` on.

        """
        with contextlib.redirect_stdout(sys.stderr):
            pydoc.help(arg)

    @line_magic
    def save_help(self, redirected):
        """Redirect output from sys.stdout to a string.

        Feeds that string directly to `help` and then returns
        the redirected stdout.
        """
        saved = io.StringIO()
        with contextlib.redirect_stdout(saved):
            help(redirected)
            return saved

    @line_magic
    def write_help(self, output_file, arg=None):
        """Write :func:`help` to a file.

        Parameters
        ----------
        output_file : str (os.Pathlike)
            File to write to.
        arg : obj, optional
            Object to run :magic:`pinfo` on.

        """
        with open(output_file, "xt") as f:
            with contextlib.redirect_stdout(f):
                help(arg)

    @line_magic
    def page_help(self, arg=None):
        """Use pydoc's pager function to display docs.

        Parameters
        ----------
        arg : obj, optional
            Object to run :magic:`pinfo` on.

        """
        if arg is None:
            return
        return pydoc.pager(pydoc.getdoc(arg))

    @line_magic
    def grep(self, obj, pattern=None):
        """Use :func:`re.compile` to match a pattern that may be in ``dir(obj)``.

        Parameters
        ----------
        obj : object
            Any object who has a large enough namespace to warrant a :command:`grep`.
        pattern : list, optional
            Unfortunately, lists are mutable objects and can't be used as
            default parameters.
            Therefore a default value of:

                pattern = ['^a-z.*$']

            Is only presented inside of the function.

        Yields
        ------
        matched_attributes : str

        """
        if obj is None:
            obj = self.shell.last_execution_result
        if pattern is None:
            pattern = ["^a-z.*$"]
        compiled = re.compile(*pattern)
        attributes = dir(obj)
        yield "\n".join(i for i in attributes if re.search(compiled, i))

    @line_magic
    def dirip(self):
        """Convenience function for ``dir(get_ipython())``.

        The list of attributes that the IPython InteractiveShell class has is
        so long that it requires a pager to see all of it.

        Which is pretty inconvenient.

        This function utilizes the IPython `SList` class to make it easier
        to work with.

        Methods of note are the :meth:`grep`.
        Attributes of note ``s``, ``l`` and ``p`` attributes.

        Examples
        ---------

        .. code-block:: python

            >>> i = HelpMagics().dirip()
            >>> i.grep('complete')
            ['Completer', 'check_complete', 'complete', 'init_completer',
            'pt_complete_style', 'set_completer_frame', 'set_custom_completer']  # +doctest.NORMALIZE_WHITESPACE

        """
        if self.shell is None:
            logging.warning(
                "Are you in in IPython? get_ipython() did not return anything"
            )
            return
        shell_list = SList(dir(self.shell))
        return shell_list

    def load(self):
        """Convenience for calling load_ipython_extension."""
        load_ipython_extension()


def load_ipython_extension(shell=None):
    """Add to the list of extensions used by IPython."""
    if shell is None:
        shell = get_ipython()
    shell.register_magics(HelpMagics)


if __name__ == "__main__":
    load_ipython_extension()
