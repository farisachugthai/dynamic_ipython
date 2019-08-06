=======
Logging
=======

`05_log`_

This uses the IPython core :class:`~IPython.core.logger.LoggingConfigurable()`
to create a :class:`logging.handler.FileHandler()` that creates one new log
file for every calendar day of the year.

Running IPython instances will continue to write to the log file if the
session continues after the point when the logfile rolls over.

If multiple sessions are started, the new instances will append onto the same
file as the older ones.

.. admonition:: Linux Only

   This only works on Linux. The Win API seemingly isn't able to
   maintain multiple connections to the same file.


05\_log module
--------------

.. automodule:: profile_default.startup.05_log
   :members:
   :undoc-members:
   :show-inheritance:

