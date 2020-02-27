.. _ipython-logger:

===========================
05_log --- IPython logger
===========================

.. currentmodule:: default_profile.startup.05_log

This uses the IPython core :class:`IPython.core.logger.LoggingConfigurable`
to create a :class:`logging.handler.FileHandler` that creates one new log
file for every calendar day of the year.

Running IPython instances will continue to write to the log file if the
session continues after the point when the logfile rolls over.

If multiple sessions are started, the new instances will append onto the same
file as the older ones.

get_history
============

Extract a session from the IPython input history.

Usage
-----

.. function:: get_history(session_number)

   TODO

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


:mod:`~default_profile.startup.05_log` module
---------------------------------------------

.. automodule:: default_profile.startup.05_log
   :members:
   :undoc-members:
   :show-inheritance:
