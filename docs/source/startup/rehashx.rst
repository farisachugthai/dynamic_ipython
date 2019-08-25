===================================================================================
`%rehashx` --- Rehash everything on $PATH and make available in the user namespace.
===================================================================================
.. magic:: rehashx

.. module:: rehashx

The IPython magic `%rehashx` allows you to reload all of your startup files
and also adds system commands to the namespace!

Insofar, I haven't noticed any significant slowdown in startup time as a result
of this, and it hugely eases utilizing IPython as a system shell.

.. automodule:: profile_default.startup.01_rehashx
   :members:
   :undoc-members:
   :show-inheritance:
