#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Move all randomly interspersed logging functions into one module."""
from datetime import datetime
import json
import logging
import os
import sys
import traceback
import warnings

import IPython
from IPython import get_ipython


def _setup_logging(log_level=logging.WARNING,
                   time_format='%(asctime)s - %(name)s - %(message)s'):
    """Enable logging. TODO: Need to add more to the formatter."""
    logger = logging.getLogger(name=__name__)
    logger.setLevel(log_level)

    stream_handler_instance = logging.StreamHandler(sys.stdout)
    stream_handler_instance.setLevel(log_level)
    formatter = logging.Formatter(time_format)
    stream_handler_instance.setFormatter(formatter)
    logger.addHandler(stream_handler_instance)
    return logger


def path_logger(logger=None):
    """Trying to put all of these functions in 1 spot. DEPRECATED."""
    warnings.warn('This function is deprecated.')

    if logger is None:
        logger = logging.getLogger(name=__name__)

    logger.setLevel(logging.WARNING)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def stream_logger(logger, log_level=logging.INFO, msg_format=None):
    """Set up a :class:`~logging.Logger()` instance, add a stream handler.

    Should do some validation on the log level there. There's a really
    useful block of code in the tutorial.

    .. admonition:: The following can't go in library logging code because
                    it takes the name of this module not where it
                    gets imported.


    .. ipython:: python
        :okexcept:

        if logger is None:
            logger = logging.getLogger(name=__name__)


    Parameters
    ----------
    logger : :class:`logging.Logger()`
        Configure a passed logger. See example below.
    level : int, optional
        Level of log records. Defaults to 20.
    msg_format : str, optional
        Representation of logging messages. Uses standard %-style string formatting.
        Defaults to ``%(asctime)s %(levelname)s %(message)s``

    Returns
    -------
    logger : :class:`logging.Logger()` instance
        Defaults to ``logging.INFO`` and '%(asctime)s %(levelname)s %(message)s'

    Examples
    --------
    >>> from profile_default.util.module_log import stream_logger
    >>> log = logging.getLogger(name=__name__)
    >>> LOGGER = stream_logger(logger=log)

    """
    assert logger is not None

    handler = logging.StreamHandler(stream=sys.stderr)

    if isinstance(log_level, int):
        level = log_level
    # TODO: Come up with else. What if they pass a string?

    logger.setLevel(level)
    handler.setLevel(level)

    if msg_format is not None:
        formatter = logging.Formatter(msg_format)
    else:
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def file_logger(filename,
                logger=None,
                shell=None,
                log_level=logging.INFO,
                msg_format=None):
    r"""Logging that emits :class:`logging.LogRecord`s to `filename`.

    Parameters
    ----------
    filename : str
        File to log :class:`logging.LogRecord`s to.
    shell : |ip|, optional
        Global instance of IPython. Can be none if not run in IPython though this
        hasn't been tested.
    log_level : int, optional
        Level of log records.
    msg_format : str, optional
        Representation of logging messages. Uses standard %-style string formatting.
        Defaults to ``%(asctime)s %(levelname)s %(message)s``

    Returns
    -------
    logger : :class:`logging.Logger()` instance

    """
    assert isinstance(shell,
                      (IPython.core.interactiveshell.InteractiveShell, None))

    if shell is not None:
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
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def json_logger():
    """Set up a logger that returns properly formatted JSON.

    Examples
    --------
    ::

        try:
            raise Exception('This is an exception')
        except:
            root_logger.exception('caught exception')

        root_logger.warn('this is a test message')
        root_logger.debug('this request_id=%d name=%s', 1, 'John')

    """
    handler = logging.StreamHandler()

    fmt = JsonFormatter()
    # add the formatter to the handler

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler.setFormatter(fmt)
    root_logger.addHandler(handler)

    return root_logger


class JsonFormatter(logging.Formatter):
    """Return valid :mod:`json` for a configured handler."""

    def format(self, record):
        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None

        return json.dumps({
            'msg':
            record.msg % record.args,
            'timestamp':
            datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'func':
            record.funcName,
            'level':
            record.levelname,
            'module':
            record.module,
            'process_id':
            record.process,
            'thread_id':
            record.thread,
            'exception':
            exc
        })
