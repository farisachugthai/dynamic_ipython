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
import time
from os import path

from IPython.core.getipython import get_ipython


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
    if shell is None:
        return
    log_dir = shell.profile_dir.log_dir
    fname = "log-" + shell.profile + "-" + time.strftime("%Y-%m-%d") + ".py"
    filename = path.join(log_dir, fname)
    notnew = path.exists(filename)
    try:
        logger = shell.logger
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
    if logger is not None:
        logmode = "append"
        log_output = True
        logger.logmode = logmode
        logger.log_output = log_output
        logger.timestamp = True
