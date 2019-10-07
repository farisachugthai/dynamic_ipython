===============================================
:mod:`~default_profile.util.module_log` module
===============================================

.. module:: default_profile.util.module_log
   :synopsis: Set up package wide logging


.. function:: file_logger

   Logging function that emits a :class:`logging.LogRecord` to ``filename``.

   Logger uses the following formatting by default.::

      %(asctime)s : %(levelname)s : %(message)s

Parameters
----------
filename : str
      File to log a :class:`logging.LogRecord` to.
logger : :class:`logging.Logger`, optional
      Instance of a :class:`logging.Logger` instantiated in the calling
      module.
shell : |ip|, optional
      Global instance of IPython. Can be **None** if not run in
      :mod:`IPython` though this hasn't been tested.
log_level : int, optional
      Level of log records.
msg_format : str, optional
      Representation of logging messages using parameters accepted by
      :class:`logging.Formatter`. Uses standard :kbd:`%` style
      string formatting.

Returns
-------
logger : :class:`logging.Logger` instance

Raises
------
AssertionError
      *shell* is not `isinstance` |ip|.

.. automodule:: default_profile.util.module_log
   :members:
   :undoc-members:
   :show-inheritance:
