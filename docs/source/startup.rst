.. _ipython_startup_readme:

=======================
IPython Startup Scripts
=======================

.. module:: IPython_README

:Author: Faris Chugthai
:Date: Apr 15, 2019

.. maybe we should more gently introduce them to whats happening

Startup Scripts
================

This repository hosts startup scripts that can be used during IPython's startup.

The scripts add well over 1000 aliases to the namespace, import commonly used
modules, configure the data analysis library Pandas, add multiple application
specific loggers, and more.


Indexed Scripts
================

As of Apr 15, 2019, the startup files present in :ref:`profile_default/startup`
are as follows:


Configuration
-------------

`01_rehashx.py`_

`04_easy_import.py`_

`05_log.py`_

`06_help_helpers.py`_

`20_aliases.py`_

`32_vi_modes.py`_

`41_numpy_init.py`_

`42_pandas_init.py`_

`50_sysexception.py`_


%rehash
-------

01_rehashx.py_

The IPython magic ``%rehash`` allows you to reload all of your startup files
and also adds system commands to the namespace!

Insofar, I haven't noticed any significant slowdown in startup time as a result
of this, and it hugely eases utilizing IPython as a system shell.

.. Development and Contributing
.. This would be a good idea though.


Easy Import
-----------

:ref:`04_easy_import`

This module simply populates the IPython namespace with frequently used modules.

A check is run to see if the user is running a new enough version of Python to
utilize the python package Pynvim instead of Neovim.

Logging
-------

:ref:`05_log`_

This uses the IPython core :class:`~IPython.core.logger.LoggingConfigurable()`
to create a FileHandler that creates one new log file for every calendar
day of the year.

Running IPython instances will continue to write to the log file if the
session continues after the point when the logfile rolls over.

If multiple sessions are started, the new instances will append onto the same
file as the older ones.

.. admonition:: This only works on Linux. The Win API seemingly isn't able to
                maintain multiple connections to the same file.


Help Helpers
-------------

Creates 2 functions in userspace to save the output of ``help(python_object)``
to a file or output to ``sys.stdout``.

Examples
--------

Create a singleton class using instance, and retrieve it::

   >>> from traitlets.config.configurable import SingletonConfigurable
   >>> class Foo(SingletonConfigurable): pass
   >>> foo = Foo.instance()
   >>> foo == Foo.instance()
   True

Create a subclass that is retrieved using the base class instance::

   >>> class Bar(SingletonConfigurable): pass
   >>> class Bam(Bar): pass
   >>> bam = Bam.instance()
   >>> bam == Bar.instance()
   True

Type:      method

Writing the Scripts
--------------------

.. admonition::

   Be careful when naming scripts that begin with digits. They will require
   extra care when you need to import them from a different module!

This problem can be solved; however, with the function
:func:`importlib.import_module()`.


Original
---------

This is the IPython startup directory

.py and .ipy files in this directory will be run *prior* to any code or files specified
via the exec_lines or exec_files configurables whenever you load this profile.

Files will be run in lexicographical order, so you can control the execution order of files
with a prefix, e.g.::

    00-first.py
    50-middle.py
    99-last.ipy

.. _01_rehashx.py: ../../profile_default/startup/01_rehashx.py
.. _04_easy_import.py: ../../profile_default/startup/04_easy_import.py
.. _05_log.py: ../../profile_default/startup/05_log.py
.. _06_help_helpers.py: ../../profile_default/startup/06_help_helpers.py
.. ignore _10_keybindings.py:  ../../profile_default/startup/10_keybindings.py
.. _20_aliases.py: ../../profile_default/startup/20_aliases.py
.. _32_vi_modes.py: ../../profile_default/startup/32_vi_modes.py
.. _41_numpy_init.py: ../../profile_default/startup/32_vi_modes.py
.. _42_pandas_init.py: ../../profile_default/startup/42_pandas_init.py
.. _50_sysexception.py: ../../profile_default/startup/50_sysexception.py
