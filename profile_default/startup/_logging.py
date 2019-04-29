#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up general logging parameters and write everything to separate files.

Logger
=======
Set up a more generalized logger. This differs from 05_log.py in that it
should be decoupled from IPython and provide reasonable defaults to fall back
on if it is executed by something other than IPython.

Formatter
----------

From :class:`logging.Formatter()`:

    Formatter instances are used to convert a LogRecord to text.

    Formatters need to know how a LogRecord is constructed. They are
    responsible for converting a LogRecord to (usually) a string which can
    be interpreted by either a human or an external system. The base Formatter
    allows a formatting string to be specified. If none is supplied, the
    the style-dependent default value, "%(message)s", "{message}", or
    "${message}", is used.

    The Formatter can be initialized with a format string which makes use of
    knowledge of the LogRecord attributes - e.g. the default value mentioned
    above makes use of the fact that the user's message and arguments are pre-
    formatted into a LogRecord's message attribute. Currently, the useful
    attributes in a LogRecord are described by:

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (if available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (if available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        return value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (if available)
    %(threadName)s      Thread name (if available)
    %(process)d         Process ID (if available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted
"""
import logging
from pathlib import Path
import time

from IPython.paths import locate_profile


def setup_ipython_logger():
    """Plug and play logging. No params so you can import and forget.

    Uses the default ``datefmt`` that comes with :class:`~logging.Formatter`
    classes. For example::

        >>> default_time_format = '%Y-%m-%d %H:%M:%S'

    Can be found under the ``__init__()`` method of the logging
    :class:`~logging.Formatter`.

    """
    ipython_profile = Path(locate_profile())
    log_title = '_log-' + time.strftime('%Y-%m-%d')

    log_name = ipython_profile.joinpath('log', '_log-' + log_title + '.log')
    logger = logging.getLogger(name=log_title)
    logger.setLevel(logging.WARNING)

    # Set the filehandler to the name of the module importing this. Don't know
    # if that's how to do it correctly so cross your fingers!
    file_handler = logging.FileHandler(log_name, encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s : %(levelname)s : %(module)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


if __name__ == "__main__":
    LOGGER = setup_ipython_logger()
