.. _customized-exceptions:

=====================
Customized Exceptions
=====================
**Source code**: `default_profile/startup/50_sysexception.py`

Debugging
==========

The help docs from IPython's core module :mod:`IPython.core.ultratb`
are phenomenally helpful.


Help on module :mod:`IPython.core.ultratb` in :mod:`IPython.core`:
==================================================================

NAME:

IPython.core.ultratb - Verbose and colourful traceback formatting.

DESCRIPTION:
------------

.. py:class:: IPython.core.ultratb.ColorTB

   I've always found it a bit hard to visually parse tracebacks in Python.  The
   ColorTB class is a solution to that problem.

   It colors the different parts of a traceback in a manner similar to what
   you would expect from a syntax-highlighting text editor.

Installation instructions for ColorTB::

    import sys,ultratb
    sys.excepthook = ultratb.ColorTB()


**VerboseTB**
=============

I've also included a port of Ka-Ping Yee's "cgitb.py" that produces all kinds
of useful info when a traceback occurs.  Ping originally had it spit out HTML
and intended it for CGI programmers, but why should they have all the fun?  I
altered it to spit out colored text to the terminal.  It's a bit overwhelming,
but kind of neat, and maybe useful for long-running programs that you believe
are bug-free.

If a crash *does* occur in that type of program you want details.

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

    The Verbose mode print all variables in the stack, which means it can
    potentially leak sensitive information like access keys, or unencrypted
    password.

    Note:  Much of the code in this module was lifted verbatim from the standard
    library module 'traceback.py' and Ka-Ping Yee's 'cgitb.py'.


Color schemes
-------------

This guy was even so kind as to give us a full explanation for the color
schemes! I never saw anything this thorough in the official docs so that's
really cool.:

    The colors are defined in the class TBTools through the use of the
    ColorSchemeTable class. Currently the following exist:

      - NoColor: allows all of this module to be used in any terminal
        (the color escapes are just dummy blank strings).
      - Linux: is meant to look good in a terminal like the Linux console
        (black or very dark background).
      - LightBG: similar to Linux but swaps dark/light colors to be more
        readable in light background terminals.
      - Neutral: a neutral color scheme that should be readable on both
        light and dark background.

    You can implement other color schemes easily, the syntax is fairly
    self-explanatory. Please send back new schemes you develop to
    the author for possible inclusion in future releases.


:func:`sys.excepthook` --- ExceptionHook
========================================

From the IPython official documentation for :mod:`IPython.core.ultratb`
and specifically the :class:`IPython.core.ultratb.AutoFormattedTB`.:

Print out a formatted exception traceback.

Optional arguments:

- out: an open file-like object to direct output to.

- ``tb_offset``: the number of frames to skip over in the stack, on a
  per-call basis (this overrides temporarily the instance's tb_offset
  given at initialization time.


.. _exception-parameters:

Parameters
----------

``*args``, ``**kwargs`` : list or dict
    The least useful call signature. Give it any length iterable.


.. _exception-see-also:

See Also
--------

:class:`IPython.core.ultratb.FormattedTB` : :class:`IPython.utils.colorable.Colorable`
    Displays all accepted keyword arguments.
    I don't know if I specified the type right but if you follow the
    :abbr:`MRU`...


.. _exception-examples:

Examples
--------

The following is the aforementioned FormattedTB class.::

    class FormattedTB(VerboseTB, ListTB):
        # Subclass ListTB but allow calling with a traceback.

        # It can thus be used as a sys.excepthook for Python > 2.1.

        # Also adds 'Context' and 'Verbose' modes, not available in ListTB.

        # Allows a tb_offset to be specified. This is useful for situations where
        # one needs to remove a number of topmost frames from the traceback (such as
        # occurs with python programs that themselves execute other python code,
        # like Python shells).

        def __init__(self, mode='Plain', color_scheme='Linux', call_pdb=False,
                     ostream=None,
                     tb_offset=0, long_header=False, include_vars=False,
                     check_cache=None, debugger_cls=None,
                     parent=None, config=None):

            # NEVER change the order of this list. Put new modes at the end:
            self.valid_modes = ['Plain', 'Context', 'Verbose', 'Minimal']
            self.verbose_modes = self.valid_modes[1:3]

            VerboseTB.__init__(self, color_scheme=color_scheme, call_pdb=call_pdb,
                               ostream=ostream, tb_offset=tb_offset,
                               long_header=long_header, include_vars=include_vars,
                               check_cache=check_cache, debugger_cls=debugger_cls,
                               parent=parent, config=config)

            # Different types of tracebacks are joined with different separators to
            # form a single string.  They are taken from this dict
            self._join_chars = dict(Plain='', Context='\n', Verbose='\n',
                                    Minimal='')
            # set_mode also sets the tb_join_char attribute
            self.set_mode(mode)
