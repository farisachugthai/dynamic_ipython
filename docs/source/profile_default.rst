===========================================
IPython Default Profile API docs
===========================================

.. highlight:: ipython
   :linenothreshold: 5

.. contents:: Table of Contents
    :local:
    :backlinks: entry
    :depth: 2


The IPython startup file can be generated with

.. code-block:: console

    ipython profile create [profilename]

and will create a configuration file at

``~/.ipython/profile_[profilename]/ipython_config.py'``.

Leaving the ``[profilename]`` argument blank will create a default profile.


:mod:`ipython_config`
---------------------

.. automodule:: profile_default.ipython_config
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`ipython_kernel_config`
----------------------------

.. literalinclude:: profile_default.ipython_kernel_config
   :linenos:


:mod:`~profile_default.startup.01_rehashx`
------------------------------------------

.. automodule:: 01_rehashx
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`~profile_default.startup.04_easy_import`
----------------------------------------------

.. automodule:: 04_easy_import
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`~profile_default.startup.05_log`
--------------------------------------

.. automodule:: 05_log
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`~profile_default.startup.06_help_helpers`
-----------------------------------------------

.. automodule:: 06_help_helpers
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`~profile_default.startup.20_aliases`
------------------------------------------

.. automodule:: 20_aliases
    :members:
    :undoc-members:
    :show-inheritance:



:mod:`~profile_default.startup.42_pandas_init`
----------------------------------------------

.. automodule:: 42_pandas_init
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`~profile_default.startup.50_sysexception`
-----------------------------------------------

.. automodule:: 50_sysexception
    :members:
    :undoc-members:

Utils
=====

:mod:`~util.timer`
------------------

.. automodule:: util.timer
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`~util.machine`
--------------------

.. automodule:: util.machine
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`~util.module_log`
-----------------------

.. automodule:: util.module_log
    :members:
    :undoc-members:
    :show-inheritance:
