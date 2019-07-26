.. IPython packages documentation master file, created by
   sphinx-quickstart on Mon Feb 25 02:48:12 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _root-index:

============================================
Welcome to IPython packages' documentation!
============================================

.. include:: ../../README.rst

.. toctree::
   :caption: Tutorial
   :maxdepth: 2

   Startup <startup>
   Keybindings <ipython_keybindings>
   Built-in Magics <magics>
   Writing Your Own Magics <custom_magics>

.. .. ifconfig:: HAS_MPL

..    .. toctree::
..       :maxdepth: 2

..       The Sphinx Extension <sphinxext>


.. toctree::
   :caption: API Docs
   :maxdepth: 1
   :titlesonly:

   IPython Shell Initialization <profile_default>
   Startup Files <profile_default.startup>
   Utility Functions <profile_default.util>
   Jupyter ZMQShell <jupyter>
   Notebook Extensions <extensions>
   Developers Notes <dev>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
