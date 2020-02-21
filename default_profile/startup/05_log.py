#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Establish a file-logger for IPython.

Collects both the input and output of every command run through the IPython
interpreter, prepends a timestamp to the commands, and save the untransformed
output to a file.

.. todo:: Logging TODOs

    - Truncate output if it exceeds a certain threshold.
        - Run **dir(np)** or **dir(pd)** a couple of times and the logs
          become swamped.
    - Possibly change that section under the shebang to also include 3
      double quotes and in the comment add system info like py version, venv,
      conda, any of the 1000000 things you could add.

"""
import functools
import logging
import reprlib
import time
from os import path, devnull
from queue import SimpleQueue

from IPython.core.getipython import get_ipython
from IPython.core.error import UsageError
from traitlets.config.configurable import LoggingConfigurable
from traitlets.config.application import LevelFormatter
from traitlets.traitlets import Instance

from default_profile import QueueHandler
from default_profile.startup import STARTUP_LOGGER


def betterConfig(name=None, parent=None):
    """Similar to :func:`logging.basicConfig`.

    Parameters
    ----------
    name : str, optional
        Name of the logger
    parent : str, optional
        Name of the parent logger. Defaults to None

    Returns
    -------
    :class:`logging.Logger()`
        Anonymous Logger instance.

    Notes
    -----
    If a :class:`logging.Filter` class is initialized with no args,
    it's default behavior is to allow all :class:`logging.LogRecords` to pass.

    """
    # Let's do some basic set up to start. Connect to other present loggers
    BASIC_FORMAT = (
        "[ %(name)s  %(relativeCreated)d ] %(levelname)s %(module)s %(message)s "
    )

    shell = get_ipython()
    log_level = logging.WARNING

    if name is None:
        name = "log_mod"

    if parent:
        better_logger = logging.getLogger(name=name).getChild(parent)
    else:
        better_logger = logging.getLogger(name=name)

    # Now let's set up a couple handlers
    better_stream = logging.StreamHandler()

    if shell.logger.logfile != "":
        logfileobject = shell.logger.logfile
        logfile = logfileobject.name
    else:
        logfile = devnull
    handler = logging.FileHandler(logfile)
    # And one of our own
    queue_handler = QueueHandler(SimpleQueue())

    better_formatter = LevelFormatter(BASIC_FORMAT + "%(highlevel)s")

    for handler in better_logger.handlers:
        handler.setLevel(log_level)
        handler.setFormatter(better_formatter)
        better_logger.addHandler(handler)

    filterer = logging.Filter("logger")
    better_logger.addFilter(filterer)

    better_logger.setLevel(logging.WARNING)
    better_logger.addFilter(logging.Filter())

    return better_logger


class VerboseLoggingConfigurable(LoggingConfigurable):
    """Tried building on the LoggingConfigurable. Doesn't work currently.

    We need to register the currently running IPython instance so it gets
    access to the config and parent attributes.
    """

    shell = Instance("InteractiveShellABC")

    def __init__(self, logger_name=None, logger_parent=None, shell=None, **kwargs):
        self.log = betterConfig(name=logger_name, parent=logger_parent)
        self.logger_name = logger_name
        self.logger_parent = logger_parent
        self.shell = shell
        if self.shell is not None:
            self.config = shell.config
            self.parent = shell.parent
        else:
            raise UsageError
        super().__init__(shell=shell, **kwargs)

    def log(self, msg, level=None):
        """Override the superclasses implementation of log.

        Allow level to be a keyword argument.

        Parameters
        ----------
        msg : str
            Message to send to the logger
        level : int, optional
            Log level. Defaults to logging.WARNING or 30.
        """
        if level is None:
            level = logging.WARNING
        self.log.log(msg, level=level)

    def __repr__(self):
        """Pretty print the truncated results of :meth:`traits`."""
        return reprlib.Repr().repr_dict(self.traits(), level=6)

    def handlers(self):
        """Returns the `logging.Handler` objects associated with the logger."""
        return self.log.handlers

    def filters(self):
        """Returns the `logging.Filter` objects associated with the logger."""
        return self.log.filters


def logging_decorator(f):
    """Create a decorator to be used around functions that need to be debugged.

    Parameters
    ----------
    f : function
        The function to decorate

    Notes
    -----
    Calls a logger

    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logging.debug("Entering %s", f.__name__)
        start = time.time()
        f(*args, **kwargs)
        end = time.time()
        logging.debug("Exiting %s in %-5.2f secs", f.__name__, end - start)

    return wrapper


def ipython_logger(shell=None):
    """Saves all commands run in the interactive namespace as valid IPython code.

    .. warning:: This is not necessarily valid python code.

    The commands are appended to a file in the directory of the
    profile in :envvar:`IPYTHONDIR` or fallback to ``~/.ipython``. This file is
    named based on the date.

    Parameters
    -----------
    shell : |ip|
        Global IPython instance.

    Raises
    ------
    RuntimeError
        If the configured logger is already logging to today's date.

    """
    shell = get_ipython()
    if shell is None:
        return

    # Setup for the logger
    log_dir = shell.profile_dir.log_dir
    fname = "log-" + time.strftime("%Y-%m-%d") + ".py"
    filename = path.join(log_dir, fname)
    notnew = path.exists(filename)
    logger = shell.logger

    try:
        logger.logstart(filename)
    except RuntimeError:
        print(" Already logging to " + logger.logfname)
        return
    # todo
    # else:
    #     extra_logger = betterConfig(name=filename, parent=STARTUP_LOGGER.name)

    if notnew:
        logger.log_write("# =================================\n")
    else:
        logger.log_write("#!/usr/bin/env python\n")
        logger.log_write("# " + fname + "\n")
        logger.log_write("# IPython automatic logging file\n")
        logger.log_write("# " + time.strftime("%H:%M:%S") + "\n")
        logger.log_write("# =================================\n")

    return logger


if __name__ == "__main__":

    ipy_logger = ipython_logger()
    if ipy_logger is not None:
        if hasattr(ipy_logger, "logmode"):
            logmode = "append"
            log_output = True
            ipy_logger.logmode = logmode
            ipy_logger.log_output = log_output
            ipy_logger.timestamp = True

    better_logger = betterConfig()
