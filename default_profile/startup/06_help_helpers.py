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
import re
import sys


def print_help(arg=None):
    """Redirect :func:`help` to ``sys.stderr``.

    Parameters
    ----------
    arg : obj, optional
        Object to run :magic:`pinfo` on.

    """
    with contextlib.redirect_stdout(sys.stderr):
        help(arg)


def save_help(redirected):
    """Redirect output from sys.stdout to a string."""
    saved = io.StringIO()
    with contextlib.redirect_stdout(saved):
        help(redirected)
        return saved


def write_help(output_file, arg=None):
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


def page_help(arg=None):
    """Using IPython's `%pinfo` magic to page information to the console.

    Also noting it's the only function in this module that actually needs
    the IPython instance so the imports were moved here.

    Parameters
    ----------
    arg : obj, optional
        Object to run :magic:`pinfo` on.
    """
    from IPython.core.getipython import get_ipython

    _ip = get_ipython()
    if hasattr(_ip, "pinfo"):
        _ip.pinfo(arg)


def grep(obj, pattern=None):
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
    if pattern is None:
        pattern = ["^a-z.*$"]
    compiled = re.compile(*pattern)
    attributes = dir(obj)
    yield "\n".join(i for i in attributes if re.search(compiled, i))


def dirip():
    """Accomodations for dir(get_ipython()).

    The list of attributes that the IPython InteractiveShell class has is
    so long that it requires a pager to see all of it.

    Which is pretty inconvenient.

    This function utilizes the IPython `SList` class to make it easier
    to work with.

    Methods of note are the :meth:`grep` and ``s``, ``l`` and ``p`` attributes.

    Examples
    ---------
    >>> from default_profile.startup import help_helpers_mod
    >>> i = help_helpers_mod.dirip()
    >>> i.grep('complete')
    ['Completer', 'check_complete', 'complete', 'init_completer', 'pt_complete_style', 'set_completer_frame', 'set_custom_completer']

    .. where did completer go?

    """
    from IPython.core.getipython import get_ipython

    shell_attributes = dir(get_ipython())
    if shell_attributes is None:
        logging.warning("Are you in in IPython? get_ipython() did not return anything")
        return
    from IPython.utils.text import SList

    shell_list = SList(shell_attributes)
    return shell_list
