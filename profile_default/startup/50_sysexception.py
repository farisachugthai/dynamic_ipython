#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Give a detailed, colored traceback and drop into pdb on exceptions.

=====================
Customized Exceptions
=====================

.. module:: 50_sysexception
   :synopsis: Specify a handler for IPython's traceback formatting.

.. versionchanged:: 06/30/2019: Testing out
                    :class:`~IPython.core.ultratb.AutoFormattedTb()`


This is excessively long but look at how cute and personal this
help doc is for :ref:`IPython.core.ultratb`!!:


Help on module IPython.core.ultratb in IPython.core:
====================================================

NAME
    IPython.core.ultratb - Verbose and colourful traceback formatting.

DESCRIPTION
    **ColorTB**

    I've always found it a bit hard to visually parse tracebacks in Python.  The
    ColorTB class is a solution to that problem.  It colors the different parts of a
    traceback in a manner similar to what you would expect from a syntax-highlighting
    text editor.

    Installation instructions for ColorTB::

        import sys,ultratb
        sys.excepthook = ultratb.ColorTB()

    **VerboseTB**

    I've also included a port of Ka-Ping Yee's "cgitb.py" that produces all kinds
    of useful info when a traceback occurs.  Ping originally had it spit out HTML
    and intended it for CGI programmers, but why should they have all the fun?  I
    altered it to spit out colored text to the terminal.  It's a bit overwhelming,
    but kind of neat, and maybe useful for long-running programs that you believe
    are bug-free.  If a crash *does* occur in that type of program you want details.
    Give it a shot--you'll love it or you'll hate it.

    .. note::

      The Verbose mode prints the variables currently visible where the exception
      happened (shortening their strings if too long). This can potentially be
      very slow, if you happen to have a huge data structure whose string
      representation is complex to compute. Your computer may appear to freeze for
      a while with cpu usage at 100%. If this occurs, you can cancel the traceback
      with Ctrl-C (maybe hitting it more than once).

      If you encounter this kind of situation often, you may want to use the
      Verbose_novars mode instead of the regular Verbose, which avoids formatting
      variables (but otherwise includes the information and context given by
      Verbose).

    .. note::

      The verbose mode print all variables in the stack, which means it can
      potentially leak sensitive information like access keys, or unencryted
      password.

    Installation instructions for VerboseTB::

        import sys,ultratb
        sys.excepthook = ultratb.VerboseTB()

    Note:  Much of the code in this module was lifted verbatim from the standard
    library module 'traceback.py' and Ka-Ping Yee's 'cgitb.py'.

----------

This guy was even so kind as to give us a full explanation for the color
schemes! I never saw anything this thorough in the official docs so that's
really cool.:

    Color schemes
    -------------

    The colors are defined in the class TBTools through the use of the
    ColorSchemeTable class. Currently the following exist:

      - NoColor: allows all of this module to be used in any terminal (the color
        escapes are just dummy blank strings).

      - Linux: is meant to look good in a terminal like the Linux console (black
        or very dark background).

      - LightBG: similar to Linux but swaps dark/light colors to be more readable
        in light background terminals.

      - Neutral: a neutral color scheme that should be readable on both light and
        dark background

    You can implement other color schemes easily, the syntax is fairly
    self-explanatory. Please send back new schemes you develop to the author for
    possible inclusion in future releases.

    Inheritance diagram:

    .. inheritance-diagram:: IPython.core.ultratb
       :parts: 3


FUNCTIONS
    eqrepr(value, repr=<function text_repr at 0x742c827ae8>)

    find_recursion(etype, value, records)
        Identify the repeating stack frames from a RecursionError traceback

        'records' is a list as returned by VerboseTB.get_records()

        Returns (last_unique, repeat_length)

    findsource(object)
        Return the entire source file and starting line number for an object.

        The argument may be a module, class, method, function, traceback, frame,
        or code object.  The source code is returned as a list of all the lines
        in the file and the line number indexes a line in that list.  An IOError
        is raised if the source code cannot be retrieved.

        FIXED version with which we monkeypatch the stdlib to work around a bug.

    fix_frame_records_filenames(records)
        Try to fix the filenames in each record from inspect.getinnerframes().

        Particularly, modules loaded from within zip files have useless filenames
        attached to their code object, and inspect.getinnerframes() just uses it.

    getargs(co)
        Get information about the arguments accepted by a code object.

        Three things are returned: (args, varargs, varkw), where 'args' is
        a list of argument names (possibly containing nested lists), and
        'varargs' and 'varkw' are the names of the * and ** arguments or None.

    inspect_error()
        Print a message about internal inspect errors.

        These are unfortunately quite common.

    is_recursion_error(etype, value, records)

    nullrepr(value, repr=<function text_repr at 0x742c827ae8>)

    text_repr(value)
        Hopefully pretty robust repr equivalent.

    with_patch_inspect(f)
        Deprecated since IPython 6.0
        decorator for monkeypatching inspect.findsource

DATA
    DEFAULT_SCHEME = 'NoColor'
    INDENT_SIZE = 8

"""
import sys

from IPython.core import ultratb


class ExceptionHook(BaseException):
    """Custom exception hook for IPython.

    From the IPython official documentation:

    Print out a formatted exception traceback.

        Optional arguments:
          - out: an open file-like object to direct output to.

          - tb_offset: the number of frames to skip over in the stack, on a
          per-call basis (this overrides temporarily the instance's tb_offset
          given at initialization time.

    Parameters
    ----------
    *args, **kwargs : The least useful call signature

    See Also
    --------
    IPython.core.ultratb.FormattedTB
        Displays all accepted keyword arguments.

    """

    instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = ultratb.AutoFormattedTB(mode='Context',
                                                color_scheme='Linux',
                                                call_pdb=True,
                                                ostream=sys.stdout)
        return self.instance(*args, **kwargs)


sys.excepthook = ExceptionHook()
