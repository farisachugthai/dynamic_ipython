#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============
IPython Logger
==============

.. module:: 05_log
    :synopsis: Create a logfile for the day and append to it if one already exists.

Establish a file-logger for IPython.

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
import logging
import os
import sys
import time
from os import path

from IPython import get_ipython


def ipython_logger_05(shell=None):
    """Saves all commands run in the interactive namespace as valid IPython code.

    .. warning:: This is not necessarily valid python code.

    The commands are appended to a file in the directory of the
    profile in :envvar:`$IPYTHONDIR` or fallback ~/.ipython. This file is
    named based on the date.

    Parameters
    -----------
    shell : |ip|
        Global IPython instance.

    Raises
    ------
    RuntimeError
        If the configured logger is already logging to todays date.

    """
    if shell is None:
        shell = get_ipython()

    log_dir = shell.profile_dir.log_dir
    fname = 'log-' + shell.profile + '-' + time.strftime('%Y-%m-%d') + ".py"
    logmode = 'append'
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
            logger.log_write(u"# =================================\n")
        else:
            logger.log_write(u"#!/usr/bin/env python\n")
            logger.log_write(u"# " + fname + "\n")
            logger.log_write(u"# IPython automatic logging file\n")
            logger.log_write(u"# " + time.strftime('%H:%M:%S') + "\n")
            logger.log_write(u"# =================================\n")
            print(" Logging to " + filename)
    except RuntimeError:
        print(" Already logging to " + logger.logfname)


if __name__ == "__main__":
    _ip = get_ipython()
    if _ip is not None:
        ipython_logger_05(_ip)
