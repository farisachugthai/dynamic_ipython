============
IPython
============

This repository contains a collection of different scripts written over the
course of the last year modifying :mod:`IPython`.

Installing
===========

All of the resources necessary for installing the contents of this repository
have been moved to the directory `tools <tools>`_.

There are environment files for Conda on both `Linux
<tools/environment_linux.txt>`_ and `Windows <tools/environment_windows.yml>`_,
`a Pipfile <tools/Pipfile>`_, `a requirements.txt <tools/requirements.txt>`_,
and another for a `development installation <tools/requirements_dev.txt>`_,
as well as a `tox.ini <tools/tox.ini>`_.

Therefore the number of files that one can use to install this repository grew
large enough that they've all been moved to their own separate folder.

Installation Assumptions
------------------------

In addition, the scripts therein make a few assumptions. One is that
the repository at `<https://github.com/farisachugthai/Gruvbox-IPython>`_
has been installed.


The other assumption, the subject of many online debates, is that the user
wants to use the text editor Neovim as their default editor.

The editor will be invoked whenever the user runs the line magic ``%edit``.

If this behavior isn't desired, the following parameter needs to be
changed like so::

   from traitlets import get_config
   c = get_config()
   c.TerminalInteractiveShell.editor = 'nvim'

Features
==========

Portability
------------

Portability was a major factor while writing these scripts.

Therefore, any script should work on:

- Ubuntu
- Android
- Windows 10

On Windows 10, the scripts have been primarily tested in powershell
windows or in a shell with either ConEmu or Cmder.

As a result, there may be unexpected behavior that arises when running the
following scripts while within in an unmodified :command:`cmd` shell.

System Agnostic Aliases
========================

To date there are well over 100 aliases manually added to the shell.

These aliases depend on the operating system used as Linux OSes will default
to a bash system shell, and Windows will have ``dosbatch`` or ``powershell``
shells.

Therefore the value of the environment variable :envvar:`shell` is checked
in addition to the observed platform.
on what platform is used to initialize the system.

``%rehashx``
-------------

The first script to run invokes ``%rehashx%`` which initializes
:mod:`IPython` with all of the commands that the system shell knows.

By invoking ``%rehashx`` at the beginning of startup, all system commands
are added as well, which regularly adds well over 1000 commands to the shell.

In addition 50+ aliases have been added for Git.

Key Bindings
============

These scripts allow for hybrid use of Vim and Emacs keybindings.

Approximately 50 Emacs keybindings are added to Vim's insert mode through
the use of :mod:`prompt_toolkit`.

The source code can be found `here`_ with documentation at `this site`_.

.. _here: profile_default/startup/32_vi_modes.py
.. _this site: https://farisachugthai.github.io/dynamic_ipython/profile_default.html#module-profile_default.startup.32_vi_mode

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
If this is not true, the ``highlighting_color`` parameter will fallback
to Monokai.

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
