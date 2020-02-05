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
from traceback import print_exc

from IPython.core.getipython import get_ipython
from IPython.core.magic import Magics, magics_class, register_line_magic, line_magic
from IPython.utils.text import SList


class UsageError(Exception):
    def __init__(self):
        super().___init__()


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
        """Redirect output from sys.stdout to a string."""
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
            Therefore a default value of::

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
        """Accomodations for dir(get_ipython()).

        The list of attributes that the IPython InteractiveShell class has is
        so long that it requires a pager to see all of it.

        Which is pretty inconvenient.

        This function utilizes the IPython `SList` class to make it easier
        to work with.

        Methods of note are the :meth:`grep` and ``s``, ``l`` and ``p`` attributes.

        Examples
        ---------
        >>> i = %dirip()
        >>> i.grep('complete')
        ['Completer', 'check_complete', 'complete', 'init_completer', 'pt_complete_style', 'set_completer_frame', 'set_custom_completer']

        .. where did completer go?

        """
        if self.shell is None:
            logging.warning(
                "Are you in in IPython? get_ipython() did not return anything"
            )
            return
        shell_list = SList(dir(self.shell))
        return shell_list


def load_ipython_extension(shell=None):
    """Add to the list of extensions used by IPython.

    ...wth happened here?

    ~/projects/dynamic_ipython/default_profile/startup/06_help_helpers.py in <module>
        176
        177
    --> 178 load_ipython_extension()
            global load_ipython_extension = <function load_ipython_extension at 0x75e606d3a0>

    ~/projects/dynamic_ipython/default_profile/startup/06_help_helpers.py in load_ipython_extension(shell=<IPython.terminal.interactiveshell.TerminalInteractiveShell object>)
        173     register_line_magic(HelpMagics.write_help)
        174     register_line_magic(HelpMagics.dirip)
    --> 175     shell.register_magics(HelpMagics)
            shell.register_magics = <bound method MagicsManager.register of <IPython.core.magic.MagicsManager object at 0x75e7612670>>
            global HelpMagics = <class 'default_profile.startup.06_help_helpers.HelpMagics'>
        176
        177

    ~/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/magic.py in register(self=<IPython.core.magic.MagicsManager object>, *magic_objects=(<class 'default_profile.startup.06_help_helpers.HelpMagics'>,))
        403             if isinstance(m, type):
        404                 # If we're given an uninstantiated class
    --> 405                 m = m(shell=self.shell)
            m = <class 'default_profile.startup.06_help_helpers.HelpMagics'>
            global shell = undefined
            self.shell = <IPython.terminal.interactiveshell.TerminalInteractiveShell object at 0x75e8c691f0>
        406
        407             # Now that we have an instance, we can register it and update the

    ~/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/magic.py in __init__(self=<default_profile.startup.06_help_helpers.HelpMagics object>, shell=<IPython.terminal.interactiveshell.TerminalInteractiveShell object>, **kwargs={'parent': <IPython.terminal.interactiveshell.TerminalInteractiveShell object>})
        533                 if isinstance(meth_name, str):
        534                     # it's a method name, grab it
    --> 535                     tab[magic_name] = getattr(self, meth_name)
            tab = {}
            magic_name = 'c'
            global getattr = undefined
            self = <default_profile.startup.06_help_helpers.HelpMagics object at 0x75e606cc10>
            meth_name = 'c'
        536                 else:
        537                     # it's the real thing

    AttributeError: 'HelpMagics' object has no attribute 'c'

    First what the fuck are those variable names? Just the letters c and m?
    Second how are so many unbound? I didnt call the function incorrectly 
    so I imagine that thats unintentional.

    """
    if shell is None:
        shell = get_ipython()

    # todo: unittest that asserts this is in _ip.magics_manager.registry after registering.
    register_line_magic(HelpMagics.grep)
    register_line_magic(HelpMagics.page_help)
    register_line_magic(HelpMagics.save_help)
    register_line_magic(HelpMagics.write_help)
    register_line_magic(HelpMagics.dirip)
    shell.register_magics(HelpMagics)


load_ipython_extension()
