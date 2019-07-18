=======================
IPython Startup Scripts
=======================

:Author: Faris Chugthai
:Date: Jul 14, 2019

Startup Scripts
================

This repository hosts startup scripts that can be used during IPython's startup.

The scripts add well over 1000 aliases to the namespace, import commonly used
modules, configure the data analysis library Pandas, add multiple application
specific loggers, and more.


Indexed Scripts
================

The startup files present in the startup directory are as follows:

Configuration
-------------

`01_rehashx`_

`04_easy_import`_

`05_log`_

`06_help_helpers`_

`20_aliases`_

`32_vi_modes`_

`41_numpy_init`_

`42_pandas_init`_

`50_sysexception`_


%rehash
-------

`01_rehashx`_

The IPython magic ``%rehash`` allows you to reload all of your startup files
and also adds system commands to the namespace!

Insofar, I haven't noticed any significant slowdown in startup time as a result
of this, and it hugely eases utilizing IPython as a system shell.

.. Development and Contributing
.. This would be a good idea though.


Importing Commonly Used Modules
-------------------------------

`04_easy_import`

This module simply populates the IPython namespace with frequently used modules.

A check is run to see if the user is running a new enough version of Python to
utilize the python package Pynvim instead of Neovim.

Logging
-------

`05_log`_

This uses the IPython core :class:`~IPython.core.logger.LoggingConfigurable()`
to create a :class:`logging.handler.FileHandler()` that creates one new log
file for every calendar day of the year.

Running IPython instances will continue to write to the log file if the
session continues after the point when the logfile rolls over.

If multiple sessions are started, the new instances will append onto the same
file as the older ones.

.. admonition:: Linux Only

   This only works on Linux. The Win API seemingly isn't able to
   maintain multiple connections to the same file.


Help Helpers
-------------

`06_log`_

Creates 2 functions in userspace to save the output of ``help(python_object)``
to a file or output to ``sys.stdout``.

Examples
========

Here we'll explain the traitlets API a little bit.

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

.. admonition:: Naming modules

   Be careful when naming scripts that begin with digits.
   They will require extra care when importing from a different module!

This problem can be solved; however, with the function
:func:`importlib.import_module()`.

In the ``__init__.py`` file in the startup directory, all modules are imported
and assigned to variables in the following manner.::

   rehashx_mod = importlib.import_module('01_rehashx')
   easy_import = importlib.import_module('04_easy_import')
   ipython_file_logger = importlib.import_module('05_log')
   help_helpers = importlib.import_module('06_help_helpers')
   user_aliases = importlib.import_module('20_aliases')
   vi_mode_keybindings = importlib.import_module('32_vi_modes')
   numpy_init = importlib.import_module('41_numpy_init')
   pandas_init = importlib.import_module('42_pandas_init')
   except_hook = importlib.import_module('50_sysexception')

This allows the modules to be used in the interactive user namespace and also
be used by other scripts.

Original
---------

This is the IPython startup directory

.py and .ipy files in this directory will be run *prior* to any code or files
specified via the exec_lines or exec_files configurables whenever you load
this profile.

Files will be run in lexicographical order, so you can control the execution
order of files with a prefix, e.g.:

    00-first.py
    50-middle.py
    99-last.ipy

.. _01_rehashx: ../../profile_default/startup/01_rehashx.py
.. _04_easy_import: ../../profile_default/startup/04_easy_import.py
.. _05_log: ../../profile_default/startup/05_log.py
.. _06_help_helpers: ../../profile_default/startup/06_help_helpers.py
.. _20_aliases: ../../profile_default/startup/20_aliases.py
.. _32_vi_modes: ../../profile_default/startup/32_vi_modes.py
.. _41_numpy_init: ../../profile_default/startup/32_vi_modes.py
.. _42_pandas_init: ../../profile_default/startup/42_pandas_init.py
.. _50_sysexception: ../../profile_default/startup/50_sysexception.py
