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
import codecs
import glob
import logging
import io

import time
from pathlib import Path
from textwrap import dedent

from traitlets.config import Bool, Configurable, LoggingConfigurable
from traitlets.config.application import LevelFormatter
from traitlets.traitlets import (
    validate,
    default,
    TraitError,
    Any,
    CInt,
    Int,
    Unicode,
    Instance,
)

import time
from os import path

from IPython import get_ipython


class LoggerManager(LoggingConfigurable):
    """Let's give cleanup a shot.

    Now with all of this effort put in to determine the mode that the user
    wants and how to best put the file where they'll expect it, it's safe to
    say that we know that we don't need a FileHandler.

    But let's add a StreamHandler and set the level. And make them configurable right?

    Attributes
    ----------
    logfile : str (os.Pathlike)
        Be careful to not set this immediately. We set it with
        :meth:`logstart` and it will raise an error if set early.
    log_raw_input : bool
        Whether to log raw or processed input.
    log_output : bool
        Whether to also log output.
    timestamp : bool
        Whether to put timestamps before each log entry.
    log_active : bool
        activity control flags
    home : str
        Not in init because it doesn't make any sense to override where
        your home directory is.

    Note
    ----
    Uses pathlib internally and externally.

    """

    # could do this. make an enum class? hm. idk.
    # logmode =
    log_raw_input = Bool(False, help="Whether to log raw or processed input").tag(
        config=True
    )
    log_output = Bool(False, help="Whether to also log output.").tag(config=True)

    timestamp = Bool(
        False, help="Whether to put timestamps before each log entry."
    ).tag(config=True)

    log_active = Bool(False, help="activity control flags").tag(config=True)

    loghead = Any(
        help=dedent(
            """
    The header in your log file.
    Only used if you're not logging in append mode to prevent
    printing a header to the same log file repetitively.
    """
        )
    ).tag(config=True)

    shell = Instance(
        "IPython.core.interactiveshell.InteractiveShellABC", allow_none=True
    )

    # handler_level = CInt(30, help="Log level for the handler").tag(config=True)

    formatter_style = Unicode(
        "%(filename)s:%(highlevel)-20s %(name)s:%(lineno)d %(message)s",
        help="How do log messages look?",
    ).tag(config=True)

    time_format = Unicode(
        "%H:%M:%S", help="Enable timestamps and you'll see what I mean."
    ).tag(config=True)

    def __init__(
        self,
        logger_name="IPython_Logger_Manager",
        logfname="Logger.log",
        logger_log_level=None,
        *args,
        **kwargs
    ):
        """New LoggerManager.

        Parameters
        ----------
        logfname : str
            Is set to the attribute 'logfile' in method :meth:`logstart`.

        """
        super().__init__(*args, **kwargs)
        self.logfname = Path(logfname)
        self.logger_name = logger_name
        self.logger_log_level = logger_log_level
        self.run()

    def __repr__(self):
        return "{r!} {:<r!}".format(self.__class__.__name__, self.logger_name)

    def log(self, *args, **kwargs):
        if self.logger_log_level == 30:
            super().log.warning(*args, **kwargs)

    def init_logger(self, override_level=None, **kwargs):
        self.logger_instance = logging.getLogger(name=self.logger_name)
        self.logger_log_level = override_level or 30
        self.logger_instance.setLevel(self.logger_log_level)

    def init_handler(self, override_level=None, **kwargs):
        self.handler = logging.StreamHandler(io.StringIO(), **kwargs)
        handler_level = override_level or 30
        self.handler.setLevel(handler_level)

    def init_formatter(
        self, override_style=None, formatter_style=None, time_format=None, **kwargs
    ):
        if override_style is not None:
            formatter_style = override_style
        self.formatter = LevelFormatter(
            fmt=formatter_style, datefmt=time_format, **kwargs
        )

    def init_filter(self, **kwargs):
        self.handler.addFilter(logging.Filter(**kwargs))

    @default("logmode")
    def _mode(self, change):
        return self.logmode

    @validate("logmode")
    def _set_mode(self, mode):
        """'logmode' is a validated property."""
        if mode not in ["append", "backup", "global", "over", "rotate"]:
            raise TraitError("invalid log mode %s given" % mode)
        self.logmode = mode

    def logappend(self):
        return self.append()

    def append(self):
        """Called when logmode is set to append."""
        return codecs.open(self.logfname, "a", encoding="utf-8")

    def backup(self, backupext="~"):
        """Create a logging file and backups as necessary at path 'target'.

        Added a backupext parameter so that can be changed.

        Also changed the logfile to be open in append mode so we don't have
        to worry about whether we have more.
        """
        if self.logfname.is_file():
            target = self.logfname / Path(backupext)
            self.logfname.rename(target)
        return codecs.open(self.logfname, "a", encoding="utf-8")

    def global_mode(self):
        """I'm changing this. Global mode shouldn't dump files in the home dir.

        Global means put it iin teh IPython dir not the profile dir.
        """
        self.logfname = Path(self.shell.ipython_dir / self.logfname)
        return codecs.open(self.logfname, "a", encoding="utf-8")

    def over(self):
        return codecs.open(self.logfname, "w", encoding="utf-8")

    @property
    def output_file(self):
        return self.logfile

    @output_file.setter
    def set_output_file(self):
        if self.logmode == "append":
            self.logfile = self.append()

        elif self.logmode == "backup":
            self.logfile = self.backup()

        elif self.logmode == "global":  # can't name a method global
            self.logfile = self.global_mode()

        elif self.logmode == "over":
            self.logfile = self.over()

        # TODO
        elif self.logmode == "rotate":
            if self.logfname.is_file():
                if Path(self.logfname / ".001~").is_file():
                    # Don't make the logic too complicated. I've set this to rotate and got
                    # pissed when i saw 11 log files from 1 session.
                    self.logfname = Path(self.logfname / ".002~")
                else:
                    self.logfname.rename(self.logfname / ".001~")
            self.logfile = codecs.open(self.logfname, "w", encoding="utf-8")

        return self.logfile

    @classmethod
    def logstart(cls):
        """Generate a new log-file with a default header."""
        if cls.logfile is not None:
            cls.shell.warn("Logging already started in this session!")
        cls.logfile = cls.set_outputfile()

        if cls.logmode != "append":
            cls.logfile.write(cls.loghead)
        cls.logfile.flush()
        cls.log_active = True

    def run(self):
        self.init_logger()
        self.init_handler()
        self.init_formatter()
        self.init_filter()


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
    log_dir = shell.profile_dir.log_dir
    fname = "log-" + shell.profile + "-" + time.strftime("%Y-%m-%d") + ".py"
    logmode = "append"
    log_output = True
    filename = path.join(log_dir, fname)
    notnew = path.exists(filename)
    logger = shell.logger
    logger.logmode = logmode
    logger.log_output = log_output
    logger.timestamp = True
    try:
        # added -t to get timestamps
        logger.logstart(filename)
        if notnew:
            logger.log_write("# =================================\n")
        else:
            logger.log_write("#!/usr/bin/env python\n")
            logger.log_write("# " + fname + "\n")
            logger.log_write("# IPython automatic logging file\n")
            logger.log_write("# " + time.strftime("%H:%M:%S") + "\n")
            logger.log_write("# =================================\n")
            print(" Logging to " + filename)
    except RuntimeError:
        print(" Already logging to " + logger.logfname)

    return logger


if __name__ == "__main__":
    _ip = get_ipython()
    logger = ipython_logger(_ip)
    logger_manager = LoggerManager()
