.. _ipython_startup_readme:

=======================
IPython Startup Scripts
=======================

.. module:: IPython_README

:Author: Faris Chugthai
:Date: Apr 15, 2019


Indexed Scripts
================
As of Apr 15, 2019, the startup files present in :ref:`profile_default/startup` are as follows:

`01_rehashx.py`_

`04_easy_import.py`_

`05_log.py`_

`06_help_helpers.py`_

`20_aliases.py`_

`42_pandas_init.py`_

`50_sysexception.py`_


%rehash
-------
:ref:`01_rehashx`

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
:ref:`05_log`




Convenience Functions
-----------------------
:ref:`IPython` provides the functions :func:`IPython.Application.initialized()`
and :func:`IPython.Application.instance()`. As a result, each script can easily
implement the following as a check to ensure that the global IPython instance
is running.

.. ipython:: python

   if __name__ == "__main__":
      from IPython import Application.initialized
      import sys

      if not Application.initialized():
         sys.exit()

.. TODO double check that what I'm saying below is true

Unfortunately, ``from IPython import Application`` may be a feature of IPython7.3,
which at the time of writing was released 3 days ago. If you don't have this
version of the module, you can alternatively run


.. ipython:: python

   from IPython.core.application import Application
   Application.initialized()


.. ipython::

   In [114]: IPython.Application.initialized?

.. code-block:: none

   Signature: IPython.Application.initialized()
   Docstring: Has an instance been created?
   File:      ~/miniconda3/lib/python3.7/site-packages/traitlets/config/configurable.py
   Type:      method


Here's the help from :attr:`IPython.application.instance`.

.. ipython::

   In [115]: IPython.Application.instance?

.. code-block:: none

   Signature: IPython.Application.instance(\*args, \*\*kwargs)
   Docstring:
   Returns a global instance of this class.
   This method create a new instance if none have previously been created
   and returns a previously created instance is one already exists.
   The arguments and keyword arguments passed to this method are passed
   on to the :meth:`__init__` method of the class upon instantiation.


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
.. _42_pandas_init.py: ../../profile_default/startup/42_pandas_init.py
.. _50_sysexception.py: ../../profile_default/startup/50_sysexception.py
