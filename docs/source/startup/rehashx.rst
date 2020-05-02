==========================================
:mod:`all_fault_handlers`
==========================================

.. currentmodule:: default_profile.startup.all_fault_handlers

As the first file in startup this file plays an important role in setting
everything else up. As a result, the first thing done is running the magic
`%rehashx`.

.. magic:: rehashx

The IPython magic `%rehashx` allows you to reload all of your startup files
and also adds system commands to the namespace!

Insofar, I haven't noticed any significant slowdown in startup time as a result
of this, and it hugely eases utilizing IPython as a system shell.

In addition 100+ aliases have been added for :command:`git`.

This is a useful place to start as any aliases that need further modification
can be overridden later.

Aliases are easy to work with as they as composed of simple data structures.

.. function:: rerun_startup()
   :noindex:

   This function can be run in an interactive session.
   The intended use case is one where the user needs to rerun the startup
   files in the ``profile_default`` startup folder.
   For various reasons, not all files in the startup foler may execute.
   This can occur if there is a syntax error in one of the files.
   After an unexpected exception is raised, the remaining files will all
   collectively not run.

   To fix that, they are all presented as arguments to the IPython magic,
   `%run` and as a result, are added to the global namespace.


Parameters
==========

``magic_name`` : str
    Name of the desired magic function, without :kbd:`%` prefix.

``line`` : str
    The rest of the input line as a single string.

``_stack_depth`` : int, optional
    Number of recursive calls to an IPython magic.


Notes
=====

:func:`IPython.core.magic.run_line_magic`
    A method of the |ip| instance to run a specific magic currently in the
    IPython.core.interactiveshell.InteractiveShell.user_ns
    or user namespace.

.. ipython::
    :verbatim:

    from IPython.core import get_ipython
    shell = get_ipython()
    shell.run_line_magic('ls', '')

Usage
======

As the help outlines above, the second required positional argument to
:func:`IPython.core.TerminalInteractiveShell.run_line_magic` is ``line``.

This is more easily understood as 'remaining arguments to the magic'.
`%rehashx` takes none, but leaving it blank causes the function call to raise
an error, so an empty `str` is passed to the function.


``_stack_depth``
----------------

The ``_stack_depth`` parameter can be understood like so:

If :func:`IPython.core.magics.run_line_magic` is called from
:func:`IPython.core.magics.magic` then
``_stack_depth`` = 2.

This is added to ensure backward compatibility for use
of :func:`IPython.core.magics.get_ipython().magic`


Fault Handlers API
===================

.. automodule:: default_profile.startup.all_fault_handlers
   :synopsis: Run the rehashx magic and begin initializing IPython startup.
   :members:
   :undoc-members:
   :show-inheritance:
