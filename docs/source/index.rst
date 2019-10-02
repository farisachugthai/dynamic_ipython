.. IPython packages documentation master file, created by
   sphinx-quickstart on Mon Feb 25 02:48:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================================
Welcome to Dynamic IPython's documentation!
============================================

:date: |today|

.. highlight:: ipython
   :linenothreshold: 3

.. moduleauthor:: Faris Chugthai

.. module:: root_index
   :synopsis: Main landing page for the documentation.


Startup Scripts
================

This repository hosts startup scripts that can be used during
IPython's startup.

The scripts add well over 1000 aliases to the namespace, import commonly used
modules, configure the data analysis library Pandas, add multiple application
specific loggers, and more.

This repository contains a collection of different scripts written over the
course of the last year modifying `IPython <docs/profile_default.html>`_
and `Jupyter <docs/jupyter.html>`_.


.. _root-extensions:

Extensions
==========

In addition this repository handles a growing number of IPython extensions.
To see more, continue reading about :ref:`extensions`.


Portability
============

Portability was a major factor while writing these scripts.

Therefore, any script should work on:

- Ubuntu
- Android
- Windows 10

On Windows 10, the scripts have been primarily tested in powershell
windows or in a shell with either ConEmu or Cmder.

As a result, there may be unexpected behavior that arises when running the
following scripts while within in an unmodified :command:`cmd` shell.


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
:func:`IPython.core.interactiveshell.register_magic_function()` and literally
every option available through the `%config` magic.

For commands that are more related to the interactive aspect of the shell,
see the following::

   >>> from IPython import get_ipython()
   >>> _ip = get_ipython()
   >>> help(_ip)  #doctest: +SKIP
   >>> dir(_ip): #doctest: +SKIP

In addition, there's an abundance of documentation online in the
form of rst docs and ipynb notebooks.


Table of Contents
==================

.. toctree::
   :caption: Tutorial
   :maxdepth: 1
   :titlesonly:

   Keybindings <ipython_keybindings>
   jobcontrol
   exceptions
   subcommands
   sphinxext
   lexer
   sphinx_api_docs
   custom_doctests
   Developers Notes <dev>

In addition the API has extensive documentation.

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :caption: API

   IPython API </startup/index>
   IPython Utilities </util/index>
   kernel
   jupyter
   extensions


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
