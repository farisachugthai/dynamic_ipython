================================
profile\_default.startup package
================================

.. highlight:: ipython
   :linenothreshold: 5

.. contents:: Table of Contents
    :local:
    :backlinks: entry
    :depth: 2

.. _startup-submodules:

Submodules
==========

`%rehashx`
----------

`01_rehashx`_

The IPython magic ``%rehash`` allows you to reload all of your startup files
and also adds system commands to the namespace!

Insofar, I haven't noticed any significant slowdown in startup time as a result
of this, and it hugely eases utilizing IPython as a system shell.


profile\_default.startup.01\_rehashx module
-------------------------------------------

.. automodule:: profile_default.startup.01_rehashx
   :members:
   :undoc-members:
   :show-inheritance:


Importing Commonly Used Modules
-------------------------------

`04_easy_import`

This module simply populates the IPython namespace with frequently used modules.

A check is run to see if the user is running a new enough version of Python to
utilize the python package Pynvim instead of Neovim.


profile\_default.startup.04\_easy\_import module
------------------------------------------------

.. automodule:: profile_default.startup.04_easy_import
   :members:
   :undoc-members:
   :show-inheritance:


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


profile\_default.startup.05\_log module
---------------------------------------

.. automodule:: profile_default.startup.05_log
   :members:
   :undoc-members:
   :show-inheritance:


Help Helpers
-------------

`06_help_helpers`_

Creates 2 functions in userspace to save the output of ``help(python_object)``
to a file or output to ``sys.stdout``.

profile\_default.startup.06\_help\_helpers module
-------------------------------------------------

.. automodule:: profile_default.startup.06_help_helpers
   :members:
   :undoc-members:
   :show-inheritance:


profile\_default.startup.20\_aliases module
-------------------------------------------

.. automodule:: profile_default.startup.20_aliases
   :members:
   :undoc-members:
   :show-inheritance:


profile\_default.startup.32\_vi\_modes module
---------------------------------------------

.. automodule:: profile_default.startup.32_vi_modes
   :members:
   :undoc-members:
   :show-inheritance:


profile\_default.startup.41\_numpy\_init module
-----------------------------------------------

.. automodule:: profile_default.startup.41_numpy_init
   :members:
   :undoc-members:
   :show-inheritance:


profile\_default.startup.42\_pandas\_init module
------------------------------------------------

.. automodule:: profile_default.startup.42_pandas_init
   :members:
   :undoc-members:
   :show-inheritance:


profile\_default.startup.50\_sysexception module
------------------------------------------------

.. automodule:: profile_default.startup.50_sysexception
   :members:
   :undoc-members:
   :show-inheritance:


.. _startup-contents:

Module contents
---------------

.. automodule:: profile_default.startup
   :members:
   :undoc-members:
   :show-inheritance:


.. _01_rehashx: ../../profile_default/startup/01_rehashx.py
.. _04_easy_import: ../../profile_default/startup/04_easy_import.py
.. _05_log: ../../profile_default/startup/05_log.py
.. _06_help_helpers: ../../profile_default/startup/06_help_helpers.py
.. _20_aliases: ../../profile_default/startup/20_aliases.py
.. _32_vi_modes: ../../profile_default/startup/32_vi_modes.py
.. _41_numpy_init: ../../profile_default/startup/32_vi_modes.py
.. _42_pandas_init: ../../profile_default/startup/42_pandas_init.py
.. _50_sysexception: ../../profile_default/startup/50_sysexception.py
