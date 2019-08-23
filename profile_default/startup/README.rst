.. _startup-readme:

=======================
IPython Startup Scripts
=======================

.. module:: startup-readme

:Author: Faris Chugthai
:Date: Mar 03, 2019


Configuration
-------------
Here's a rough outline of what's going on in this directory.

As of March 3rd, the files present are as follows:

`04_easy_import.py`_

`05_log.py`_

`06_help_helpers.py`_

`20_aliases.py`_

`32_vi_modes`.py_

`42_pandas_init.py`_

`50_sysexception.py`_


%rehashx
--------

`01_rehashx.py`_

The :mod:`IPython` magic ``%rehashx`` allows you to reload all of your startup
files. This is convenient when working with a new class based module, and the
``%reset`` magic has wiped out all of your aliases.

However the beautiful part of this magic:

It adds every executable listed under the environment variable :envvar:`$PATH`.
to the namespace!

Therefore, the first script that runs in the startup directory is a simple script
that invokes ``%rehashx``.

Insofar, I haven't noticed any significant slowdown in startup time as a result
of this, and it hugely eases utilizing :mod:`IPython` as a system shell.


Convenience Functions
-----------------------
:ref:`IPython` provides the functions :func:`IPython.Application.initialized()`
and :func:`IPython.Application.instance()`. As a result, each script can easily
implement the following as a check to ensure that the global :mod:`IPython`
instance is running.

.. ipython:: python

   if __name__ == "__main__":
      from IPython import Application
      import sys

      if not Application.initialized():
         sys.exit()


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

.. ipython::

   In [115]: IPython.Application.instance?

This provides the following signature:

.. code-block:: none

   Signature: IPython.Application.instance(*args, **kwargs)
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


Original
---------

This is the IPython startup directory

.py and .ipy files in this directory will be run *prior* to any code or
files specified via the exec_lines or exec_files configurables whenever
you load this profile.

Files will be run in lexicographical order, so you can control the
execution order of files with a prefix, e.g.

.. code-block:: shell

    00-first.py
    50-middle.py
    99-last.ipy

.. _01_rehashx.py: ./01_rehashx.py
.. _04_easy_import.py: ./04_easy_import.py
.. _05_log.py: ./05_log.py
.. _06_help_helpers.py:  ./10_keybindings.py
.. _20_aliases.py: ./20_aliases.py
.. _32_vi_modes.py: ./32_vi_modes.py
.. _42_pandas_init.py: ./42_pandas_init.py
.. _50_sysexception.py: ./50_sysexception.py
