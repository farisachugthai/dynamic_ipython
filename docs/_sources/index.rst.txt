.. IPython packages documentation master file, created by
   sphinx-quickstart on Mon Feb 25 02:48:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================================
Welcome to Dynamic IPython's documentation!
============================================

:date: |today|

.. highlight:: ipython

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
course of the last year modifying `IPython <docs/profile_default.html>`_.


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


Installation
============

This repository can be installed in the following manner.:

.. ipython::
   :verbatim:

   python setup.py build
   pip install -U -e .

However, that unfortunately assumes one has admin access to wherever pip
installs files globally, and that the :command:`python` command points to
python3.7. In most cases it does not.

If one has :command:`pipenv` installed, an easier installation could be

.. ipython::
   :verbatim:

   pipenv install -e .

If a non-pipenv installation is desired for some reason, a fully specified
installation could look like.

.. ipython::
   :verbatim:

   python3.7 setup.py build
   python3.7 -m pip install -U --user pip -e .

As one can see this gets complicated very quickly, and as a result,
installation via pipenv is the recommended method.


See Also
==========

For further reading, feel free to see the output of any of the following::

    >>> from IPython.core.interactiveshell import InteractiveShell
    >>> help(InteractiveShell)

Which features descriptions of functions relevant to startup such as
:func:`IPython.core.interactiveshell.register_magic_function` and literally
every option available through the `%config` magic.

For commands that are more related to the interactive aspect of the shell,
see the following::

    >>> from IPython import get_ipython
    >>> _ip = get_ipython()
    >>> help(_ip)  # doctest: +SKIP
    >>> dir(_ip):  # doctest: +SKIP

In addition, there's an abundance of documentation online in the
form of rst docs and :abbr:`ipynb` notebooks.


Table of Contents
==================

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :caption: API

   Sphinx Extensions <sphinxext/index>
   IPython Startup <startup/index>
   IPython Utilities </util/index>
   extensions
   jobcontrol
   todo
   Developers Notes <dev>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
