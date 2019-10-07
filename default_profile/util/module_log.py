#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===================
Prepackaged Loggers
===================

Set up easily instantied :class:`logging.Logger` instances.

Create a few formatters and logging instances that can be easily
imported and utilized across the package.

Currently :func:`~default_profile.util.module_log.stream_logger`
is the easiest and most oft used entry point in this module.

.. doctest::

    >>> import logging
    >>> import default_profile
    >>> from default_profile.util import module_log
    >>> module_log.stream_logger(logging.getLogger(__name__))


"""
from datetime import datetime
import json
import logging
import os
import sys
import traceback
import warnings

import IPython
from IPython import get_ipython


def stream_logger(logger, log_level=logging.INFO, msg_format=None):
    """Set up a :class:`logging.Logger` instance, add a stream handler.

    Should do some validation on the log level there. There's a really
    useful block of code in the tutorial.

    Parameters
    ----------
    logger : :class:`logging.Logger`
        Configure a passed logger. See example below.
    log_level : int, optional
        Level of log records. Defaults to 20.
    msg_format : str, optional
        Representation of logging messages. Uses standard :kbd:`%` style string
        formatting. Defaults to ``%(asctime)s %(levelname)s %(message)s``

    Returns
    -------
    logger : :class:`logging.Logger()` instance
        Defaults to ``logging.INFO`` and '%(asctime)s : %(levelname)s : %(message)s : '

    Examples
    --------
    >>> import logging
    >>> from default_profile.util.module_log import stream_logger
    >>> LOGGER = stream_logger(logging.getLogger(name=__name__))

    """

    if isinstance(logger, str):
        logger = logging.getLogger(logger)
    elif isinstance(logger, logging.Logger):
        pass

    # TODO: Come up with else. What if they pass a string?
    if isinstance(log_level, int):
        level = log_level

    logger.setLevel(level)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(level)

    if msg_format is not None:
        formatter = logging.Formatter(msg_format)
    else:
        formatter = logging.Formatter(
            '%(asctime)s : %(levelname)s : %(message)s : '
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def file_logger(
        filename, logger=None, shell=None, log_level=logging.INFO,
        msg_format=None
):
    """Removed docstring because it wouldn't stop emitting errors."""
    assert isinstance(
        shell, (IPython.core.interactiveshell.InteractiveShell, None)
    )

    if shell is None:
        shell = get_ipython()

    logdir = shell.profile_dir.log_dir

    log_file = os.path.join(logdir, filename)
    handler = logging.FileHandler(log_file)

    handler.setLevel(log_level)
    if logger is None:
        logger = logging.getLogger(name=__name__)

    logger.setLevel(log_level)

    if msg_format is not None:
        formatter = logging.Formatter(msg_format)
    else:
        formatter = logging.Formatter(
            '%(asctime)s : %(levelname)s : %(message)s : '
        )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def json_logger(logger=None, json_formatter=None):
    """Set up a logger that returns properly formatted JSON.

    Parameters
    ----------
    logger : str or :class:`logging.Logger`, optional
        Either a named Logger instance or the string representing the desired instance
    json_formatter : :class:`logging.Formatter`, optional
        JSONFormatter instance.
        Included in the listed parameters to be explicit; however, it's
        probably easier to not include the parameter as one is configured
        in the function anyway.

    Returns
    -------
    root_logger : :class:`logging.Logger`
        Instance of a :class:`logging.Logger()`.

    Examples
    --------
    >>> import logging
    >>> from default_profile.util.module_log import json_logger, JsonFormatter
    >>> root_logger = json_logger(JsonFormatter=JsonFormatter())
    >>> root_logger.warn('this is a test message')
    >>> root_logger.debug('this request_id=%d name=%s', 1, 'John')

    """
    handler = logging.StreamHandler()

    if not json_formatter:
        fmt = JsonFormatter()
    else:
        fmt = json_formatter

    if not logger:
        root_logger = logging.getLogger()
    elif isinstance(logger, str):
        root_logger = logging.getLogger(name=logger)
    elif isinstance(logger, logging.Logger):
        root_logger = logger
    else:
        raise Exception

    root_logger.setLevel(logging.DEBUG)
    handler.setFormatter(fmt)
    handler.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    return root_logger


class JsonFormatter(logging.Formatter):
    """Return valid :mod:`json` for a configured handler."""

    def format(self, record):
        """Format a :class:`logging.LogRecord()` from an :exc:Exception."""
        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None

        return json.dumps(
            {
                'msg': record.msg % record.args, 'timestamp':
                    datetime.utcfromtimestamp(record.created).isoformat() +
                    'Z',
                'func': record.funcName, 'level': record.levelname, 'module':
                    record.module, 'process_id': record.process, 'thread_id':
                        record.thread, 'exception': exc
            }
        )


def betterConfig():
    """Similar to logging.basicConfig().

    Parameters
    ----------
    None

    Returns
    -------
    :class:`logging.Logger()`
        Anonymous Logger instance.

    Notes
    -----
    If a :class:`logging.Filter` class is initialized with no args,
    it's default behavior is to allow all :class:`logging.LogRecords` to pass.

    """
    logging.BASIC_FORMAT = '%(created)f : %(levelname)s : %(module)s : %(message)s : '
    better_logger = logging.getLogger()
    better_logger.setLevel(logging.WARNING)

    better_stream = logging.StreamHandler()
    better_stream.setLevel(logging.WARNING)
    better_logger.addHandler(better_stream)

    better_formatter = logging.Formatter(logging.BASIC_FORMAT)
    better_stream.setFormatter(better_formatter)

    better_logger.setFilterer(logging.Filter())

    return better_logger
