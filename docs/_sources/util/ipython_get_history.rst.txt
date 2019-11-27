=================================================
:mod:`~default_profile.util.ipython_get_history`
=================================================

.. currentmodule:: default_profile.util.ipython_get_history

Extract a session from the IPython input history.

Usage
-----
.. program:: ipython_get_history.py sessionnumber [outputfile]

If 'outputfile' is not given, the relevant history is written to
:data:`sys.stdout.` If 'outputfile' has a *.py* extension,
the translated history (without IPython's special syntax) will be extracted.


Examples
--------

.. code-block:: bash

  python3 ipython-get-history.py 57 record.ipy

This script is a simple demonstration of
:class:`IPython.core.history.HistoryAccessor`. It should be possible
to build much more flexible and powerful tools to browse and pull from the
history database.

So this is a rewrite of that history accessor since IPython's handling of
history sessions out of the box is oddly limited.

Let's ignore the direct calls to sys.argv and combine argparse and the
magic_argparse functions to make something more durable and useful.



.. automodule:: default_profile.util.ipython_get_history
   :synopsis: Showcase a use for IPython's HistoryAccessor class and write SQL.
   :members:
   :undoc-members:
   :show-inheritance:

