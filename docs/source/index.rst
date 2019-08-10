.. IPython packages documentation master file, created by
   sphinx-quickstart on Mon Feb 25 02:48:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _root-index:

============================================
Welcome to Dynamic IPython's documentation!
============================================

:date: |today|

.. highlight:: ipython

.. moduleauthor:: Faris Chugthai

.. module:: root_index
   :synopsis: Index


Startup Scripts
================

This repository hosts startup scripts that can be used during IPython's startup.

The scripts add well over 1000 aliases to the namespace, import commonly used
modules, configure the data analysis library Pandas, add multiple application
specific loggers, and more.

This repository contains a collection of different scripts written over the
course of the last year modifying `IPython <docs/profile_default.html>`_
and `Jupyter <docs/jupyter.html>`_.

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

The intent was to create a system that worked on any relatively
modern platform.

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

.. toctree::
   :caption: Tutorial
   :maxdepth: 2

   Keybindings <ipython_keybindings>
   Built-in Magics <magics>
   Writing Your Own Magics <custom_magics>
   exceptions

.. ifconfig:: HAS_MPL

   .. toctree::
      :maxdepth: 2

      The Sphinx Extension <sphinxext>


.. toctree::
   :caption: API Docs
   :maxdepth: 1
   :titlesonly:

   IPython Shell Initialization <profile/index>
   Jupyter ZMQShell <jupyter>
   Notebook Extensions <extensions>
   Contributors Notes <dev>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
