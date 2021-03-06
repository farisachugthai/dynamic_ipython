#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Establish a file-logger for IPython.

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

.. note:: Windows Users

    Simulataneous IPython processes may throw.

.. code-block:: py3tb

   PermissionError: [WinError 32]
   The process cannot access the file because it is being used by another process:
   'C:\\Users\\fac\\.ipython\\profile_default\\log\\log-2020-02-26.py' ->
   'C:\\Users\\fac\\.ipython\\profile_default\\log\\log-2020-02-26.py.001~'

"""
import codecs
import functools
import json
import logging
import os
import pprint
import reprlib
import sqlite3
import sys
import time
import traceback

from datetime import datetime
from itertools import groupby
from logging.handlers import MemoryHandler
from pathlib import Path
try:
    from _queue import SimpleQueue
except ImportError:
    from queue import _PySimpleQueue as SimpleQueue

from IPython.core.getipython import get_ipython
from IPython.core.history import HistoryAccessor

# from IPython.core.history import HistorySavinThread, HistoryManager
from IPython.paths import get_ipython_dir
from traitlets.config.configurable import LoggingConfigurable
from traitlets.config.application import LevelFormatter
from traitlets.traitlets import Instance

from default_profile.ipython_config import UsageError


class NoUnNamedLoggers(NotImplementedError):
    """Raise this error if the logger a function was called with was anonymous."""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args)

    def __call__(self):
        return "".format("You did not provide a name for the logger.")


def print_history(hist_file=None):
    """Write the contents of the running shell's :mod:`sqlite` history.

    Parameters
    ----------
    hist_file : str (`os.Pathlike`), optional
        Path to history file. Assume default profile's history.

    """
    if hist_file is None:
        hist_file = f"{get_ipython_dir()}/profile_default/history.sqlite"

        if not os.path.exists(hist_file):
            return

    with sqlite3.connect(hist_file) as con:
        c = con.cursor()
        c.execute(
            "SELECT count(source_raw) as csr,\
                  source_raw FROM history\
                  GROUP BY source_raw\
                  ORDER BY csr"
        )
        result = c.fetchall()
        pprint.pprint(result, compact=True)
        c.close()
        return result


# TODO: isn't working
def get_history(session_number=None, raw=True, profile=None):
    if profile is None:
        profile = "default"
    sys.stdout.write("# coding: utf-8\n")

    # Profiles other than 'default' can be specified here with a profile= argument:
    hist = HistoryAccessor(profile)

    if session_number is None:
        session_number = 1
    running_tally = []
    for session, lineno, cell in hist.get_range(session=session_number, raw=raw):
        cell = cell.encode("utf-8")  # This line is only needed on Python 2.
        sys.stdout.write(cell + "\n")
        # we could even
        running_tally.append({session: {lineno: cell}})
    return running_tally


def betterConfig(name=None, parent=None):
    """Similar to :func:`logging.basicConfig`.

    Parameters
    ----------
    name : str, optional
        Name of the logger to return.
    parent : str, optional
        Name of the parent logger. I.E. One can provide an already
        initialized logger to this function and it will create a child logger.
        Defaults to None.

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

    name = "log_mod" if name is None else name

    if parent:
        if isinstance(
            parent, logging.Logger
        ):  # we needed the parent's name not the instance
            parent = parent.name
        better_logger = logging.getLogger(name=name).getChild(parent)
    else:
        better_logger = logging.getLogger(name=name)

    # Now let's set up a couple handlers
    better_stream = logging.StreamHandler()
    better_logger.addHandler(better_stream)

    # literally no idea if this is a good number or not
    handler = MemoryHandler(100, target=sys.stderr)
    better_logger.addHandler(handler)
    better_formatter = LevelFormatter(BASIC_FORMAT + "%(highlevel)s")

    for handler in better_logger.handlers:
        handler.setLevel(log_level)
        handler.setFormatter(better_formatter)

    filterer = logging.Filter("logger")
    better_logger.addFilter(filterer)

    better_logger.setLevel(logging.WARNING)
    better_logger.addFilter(logging.Filter())

    return better_logger


class ConfigurableLogger(LoggingConfigurable, logging.Logger):
    logger: logging.Logger
    name = __name__
    level = 30

    def __init__(self, logger=None, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger

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
        self.logger.log(msg, level=level)

    def __repr__(self):
        """Pretty print the truncated results of :meth:`traits`."""
        return f"<{self.__class__.__name__}> {reprlib.Repr().repr(self.traits())}"


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


def ipython_logger():
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
    shell.logger.logmode = "append"
    log_dir = shell.profile_dir.log_dir
    fname = "log-" + time.strftime("%Y-%m-%d") + ".py"
    filename = os.path.join(log_dir, fname)
    notnew = os.path.exists(filename)
    logger = shell.logger

    try:
        logger.logstart(filename)
    except RuntimeError:
        print(" Already logging to " + logger.logfname)
        return
    except PermissionError as e:
        try:
            if hasattr(e, WindowsError):
                print(" Already logging to " + logger.logfname)
                return
            else:
                traceback.print_exc(e)
        except:
            breakpoint()

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


class MyHistoryAccessor(HistoryAccessor):
    """ Modified HistoryAccessor to fetch the whole ipython history across all sessions """

    def get_tail(self, n=10, raw=True, output=False, include_latest=False):
        """Get the last n lines from the history database.

        Parameters
        ----------
        n : int
            The number of lines to get
        raw, output : bool
            See :meth:`get_range`
        include_latest : bool
            If False (default), n+1 lines are fetched, and the latest one
            is discarded. This is intended to be used where the function
            is called by a user command, which it should not return.

        Returns
        -------
        Tuples as :meth:`get_range`

        """
        self.writeout_cache()
        if not include_latest:
            n += 1
        if n is None:
            cur = self._run_sql(
                "ORDER BY session DESC, line DESC LIMIT ?", (n,), raw=raw, output=output
            )
        else:
            cur = self._run_sql(
                "ORDER BY session DESC, line DESC", (), raw=raw, output=output
            )
        if not include_latest:
            return reversed(list(cur)[1:])
        return reversed(list(cur))


def rem_dups(lst):
    # OrderedSet would be nicer, but for simplicity we use this approach
    return [key for key, _ in groupby(lst)]


def access_all_history(*args):
    # Syntax: ipythonhist [LAST X ITEMS]
    hist = MyHistoryAccessor()
    history = list(hist.get_tail())
    history = rem_dups(history)

    if len(args) > 0:
        head = int(args[0])
        for entry in history[-head:]:
            print(entry[2])
    else:
        for entry in history:
            print(entry[2])


def stream_logger(logger, log_level=logging.INFO, msg_format=None):
    """Set up a :class:`logging.Logger` instance, add a stream handler.

    Should do some validation on the log level there. There's a really
    useful block of code in the tutorial.

    Parameters
    ----------
    logger : str
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
    >>> from default_profile.startup.file_logger import stream_logger
    >>> LOGGER = stream_logger(logging.getLogger(name=__name__))

    """
    if isinstance(logger, str):
        logger = logging.getLogger(logger)
    elif isinstance(logger, logging.Logger):
        pass
    else:
        raise NoUnNamedLoggers()

    # TODO: Come up with else. What if they pass a string?
    if isinstance(log_level, int):
        level = log_level

    logger.setLevel(level)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(level)

    if msg_format is None:
        msg_format = "%(asctime)s %(levelname)s  %(message)s\n"

    formatter = logging.Formatter(msg_format)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def file_logger(
    filename, logger=None, shell=None, log_level=logging.INFO, msg_format=None
):
    assert isinstance(shell, (IPython.core.interactiveshell.InteractiveShell, None))

    if shell is None:
        shell = get_ipython()

    logdir = shell.profile_dir.log_dir
    log_file = Path(logdir).joinpath(filename)
    handler = logging.FileHandler(log_file)
    handler.setLevel(log_level)
    if logger is None:
        logger = logging.getLogger(name=__name__)

    logger.setLevel(log_level)

    if msg_format is not None:
        formatter = logging.Formatter(msg_format)
    else:
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s : ")

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def json_logger(logger=None, json_formatter=None):
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
                "msg": record.msg % record.args,
                "timestamp": datetime.utcfromtimestamp(record.created).isoformat()
                + "Z",
                "func": record.funcName,
                "level": record.levelname,
                "module": record.module,
                "process_id": record.process,
                "thread_id": record.thread,
                "exception": exc,
            }
        )


if __name__ == "__main__":

    ipy_logger = ipython_logger()
    if ipy_logger is not None and hasattr(ipy_logger, "logmode"):
        logmode = "append"
        log_output = True
        ipy_logger.logmode = logmode
        ipy_logger.log_output = log_output
        ipy_logger.timestamp = True
        # I think this has to be set
        ipy_logger.log_active = True

    # Don't use name=__name__ here or it'll dump a log file in your cwd
    # better_logger = betterConfig(parent=STARTUP_LOGGER)
