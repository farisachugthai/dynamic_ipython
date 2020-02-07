.. _pandas-csv:

============
Pandas CSV
============

.. currentmodule:: default_profile.extensions.pd_csv

.. magic:: pd_csv

Magic that reads in a string and parses it as a :mod:`CSV` with :mod:`pandas`.

Example of creating a magic from **IPython Interactive Computing and
Visualization Cookbook by Cyrille Roussou.**

The example specifically is from pages 32 to 35.

It also shows the following simpler example:

.. ipython::

    In [1]: from IPython.core.magic import (register_line_magic, register_cell_magic)
    In [2]: @register_line_magic
            def hello(line):
                if line == 'french':
                    print("Salut tout le monde!")
                else:
                    print("Hello world!")


:mod:`~default_profile.extensions.pd_csv` API docs
===================================================

.. automodule:: default_profile.extensions.pd_csv
   :synopsis: Utiilize pandas to load data in a :mod:`csv` file.
   :members:
   :undoc-members:
   :show-inheritance:

