.. _ipython-logger:

===========================
File Logger
===========================

.. currentmodule:: default_profile.startup.file_logger


Summary
========
Set up easily instantiated :class:`logging.Logger` instances.

Create a few formatters and logging instances that can be easily
imported and utilized across the package.

Currently :func:`stream_logger` is the easiest and most oft used entry point
in this module.

Exceptions
===========
:exc:`NoUnNamedLoggers`
    Exception raised when a function in this module is called without a
    name argument for the logger.


Stream Logging
==============
.. function:: stream_logger(logger, log_level=logging.INFO, msg_format=None)
   :noindex:

   Returns a fully functional Logger instance for ready use.


File Logging
================
.. function:: file_logger(filename, logger=None, shell=None, log_level=None, msg_format=None
   :noindex:

   Logging function that emits a :class:`logging.LogRecord` to ``filename``.
   Logger uses the following formatting by default.:

      %(asctime)s : %(levelname)s : %(message)s

   :param filename: str
      File to log a :class:`logging.LogRecord` to.

   :param logger: :class:`logging.Logger`, optional
      A :class:`logging.Logger` instantiated in the calling module.

   shell : |ip|, optional
      Global instance of IPython. Can be **None** if not run in
      :mod:`IPython` though this hasn't been tested.

   log_level : int, optional
      Level of log records.

   msg_format : str, optional
      Representation of logging messages using parameters accepted by
      :class:`logging.Formatter`. Uses standard :kbd:`%` style
      string formatting.

   :param logger: :class:`logging.Logger` instance

   :raises AssertionError:
      *shell* is not `isinstance` |ip|.


JSON logger
===========
Set up a logger that returns properly formatted JSON.

Parameters
----------
logger : str or :class:`logging.Logger`, optional
   Either a named Logger instance or the string representing the desired instance

json_formatter : :class:`logging.Formatter`, optional `JSONFormatter` instance.
   Included in the listed parameters to be explicit; however, it's
   probably easier to not include the parameter as one is configured
   in the function anyway.

Returns
-------
root_logger : :class:`logging.Logger`
   Instance of a :class:`logging.Logger()`.


Remainder
==========
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
   :noindex:

   Queries the IPython database for history entries.

Examples
--------
.. code-block:: bash

  python3 ipython-get-history.py 57 record.ipy


Summary for Logger
------------------
This script is a simple demonstration of
:class:`IPython.core.history.HistoryAccessor`. It should be possible to build
much more flexible and powerful tools to browse and pull from the history
database. This is a rewrite of that history accessor since IPython's handling of
history sessions out of the box is oddly limited.

Let's ignore the direct calls to sys.argv and combine argparse and the
magic_argparse functions to make something more durable and useful.


File Logger API
===============

.. automodule:: default_profile.startup.file_logger
   :synopsis: Easy to use standardized package-wide logging.
   :members:
   :undoc-members:
   :show-inheritance:
