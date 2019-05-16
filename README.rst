============
IPython
============

This repository contains a collection of different scripts written over the
course of the last year modifying :mod:`IPython`.

Motivation
===========

The intent was to create a system that worked on any relatively modern platform.

I regularly use :mod:`IPython` as a system shell in comparison to the
typical Bash shell that Unix OSes provide. While a terminal provides a
huge number of powerful commands and the ability to pipe them together,
Bash still has a number of inconsistencies and oddities in its behavior.

As a result I've created a few `extensions <extensions/README.rst>`_ and
written a few scripts that are run during the initialization stage of
IPython's `startup <profile_default/startup/README.rst>`_.

Features
----------

The first script to run invokes ``%rehashx%`` which initializes
:mod:`IPython` with all of the commands that the system shell knows.

Portability
============

Portability was a major factor while writing these scripts.

Therefore, any script should work on:

- Ubuntu
- Android
- Windows 10

On Windows 10, the scripts have been primarily tested in powershell
windows or Conemu.

As a result, there may be unexpected behavior that arises when using
these modifications while within :command:`cmd`.

Installing
===========
In addition, the scripts therein make a few assumptions. One is that the repository
at `<https://github.com/farisachugthai/Gruvbox-IPython>`_ has been installed.

If this is not true, the ``highlighting_color`` parameter will need to be changed.

Another would be that the user wants to use Nvim as their default editor.
Once again this will need to be changed if not true.
However, these are minor details are can be configured with relatively
little effort.

As a matter of fact, this README is currently being written from within Emacs!

.. The IPython Interactive Shell
.. -----------------------------


System Agnostic Aliases
========================
To date there are well over 100 aliases manually added to the shell depending
on what platform is used to initialize the system.

By invoking ``%rehashx`` at the beginning of startup, all system commands
are added as well, which regularly add well over 1000 commands to the shell.

In addition 50+ aliases have been added for Git.


See Also
==========
For further reading, feel free to see the output of any of the following::

   >>> from IPython.core.interactiveshell import InteractiveShell
   >>> help(InteractiveShell)

Which features descriptions of functions relevant to startup such as
:func:`~IPython.core.interactiveshell.register_magic_function()` and literally
every option available through the ``%config`` magic.

For commands that are more related to the interactive aspect of the shell,
see the following::

   >>> from IPython import get_ipython()
   >>> _ip = get_ipython()
   >>> help(_ip)
   >>> dir(_ip)

In addition, there's an abundance of documentation online in the
form of rst docs and ipynb notebooks.
