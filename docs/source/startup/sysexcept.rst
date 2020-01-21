:orphan:

.. _customized-exceptions:

=====================
Customized Exceptions
=====================

In this module we'll define our own exception hook for IPython.


Debugging
==========

The help docs from IPython's core module :mod:`IPython.core.ultratb`
are phenomenally helpful.


Help on module :mod:`IPython.core.ultratb` in :mod:`IPython.core`:
==================================================================

NAME:

:mod:`IPython.core.ultratb` - Verbose and colourful traceback formatting.

DESCRIPTION:
------------

.. py:class:: IPython.core.ultratb.ColorTB

   I've always found it a bit hard to visually parse tracebacks in Python.  The
   ColorTB class is a solution to that problem.

   It colors the different parts of a traceback in a manner similar to what
   you would expect from a syntax-highlighting text editor.

Installation instructions for `~IPython.core.ultratb.ColorTB`::

    import sys,ultratb
    sys.excepthook = ultratb.ColorTB()


:class:`IPython.core.ultratb.VerboseTB`
-----------------------------------------

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

    The colors are defined in the class :class:`TBTools` through the use of the
    :class:`ColorSchemeTable` class. Currently the following exist:

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
---------

:class:`IPython.core.ultratb.FormattedTB` : :class:`IPython.utils.colorable.Colorable`
    Displays all accepted keyword arguments.
    I don't know if I specified the type right but if you follow the
    :abbr:`MRU`...


Interface with the user
-----------------------

With all of that background on how to traceback handlers work, now
let's use some of that knowledge.

One can set the following variables on the running |ip|.:

* custom_exceptions --- set by the :meth:`set_custom_exc`

* xmode --- show tracebacks in different formats

For try/excepts there are.:

* last_execution_result and last_execution_succeeded

|ip| has the methods.:

* call_pdb

* debugger

Instances from ultratb
~~~~~~~~~~~~~~~~~~~~~~~~

In addition there's the instance ``InteractiveTB`` that's bound to the shell.

This is an instance of a `VerboseTB`.

However note the InteractiveTB being mentioned in these docstrings.:

   In [141]: _ip.excepthook?
   Signature: _ip.excepthook(etype, value, tb)

   Docstring:

.. code-block:: rst

   One more defense for GUI apps that call sys.excepthook.
   GUI frameworks like wxPython trap exceptions and call
   sys.excepthook themselves.  I guess this is a feature that
   enables them to keep running after exceptions that would
   otherwise kill their mainloop. This is a bother for IPython
   which excepts to catch all of the program exceptions with a try:
   except: statement.

   Normally, IPython sets sys.excepthook to a CrashHandler instance, so if
   any app directly invokes sys.excepthook, it will look to the user like
   IPython crashed.  In order to work around this, we can disable the
   CrashHandler and replace it with this excepthook instead, which prints a
   regular traceback using our InteractiveTB.  In this fashion, apps which
   call sys.excepthook will generate a regular-looking exception from
   IPython, and the CrashHandler will only be triggered by real IPython
   crashes.

   This hook should be used sparingly, only in places which are not likely
   to be true IPython errors.
   Type:      method

   self.showtraceback((etype, value, tb), tb_offset=0)
   _ip.showtraceback(exc_tuple=None,filename=None,tb_offset=None,exception_only=False,running_compiled_code=False,
   Display the exception that just occurred.

   Docstring:

   If nothing is known about the exception, this is the method which
   should be used throughout the code for presenting user tracebacks,
   rather than directly invoking the InteractiveTB object.

   A specific showsyntaxerror() also exists, but this method can take
   care of calling it if needed, so unless you are explicitly catching a
   SyntaxError exception, don't try to analyze the stack manually and
   simply call this method.


.. seealso:: init_traceback_handlers

