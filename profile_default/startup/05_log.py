#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a logfile for the day and append to it if one already exists.

==============
IPython Logger
==============

.. module:: 05_log
    :synopsis: Establish a file-logger for IPython.

.. highlight:: ipython3

Collects both the input and output of every command run through the IPython
interpreter and prepends a timestamp to commands.

The timestamp is particularly convenient for concurrent instances of IPython.

.. versionchanged:: Version Changed

    :func:`IPython.core.interactiveshell.InteractiveShell.magic()`
    to :func:`IPython.core.interactiveshell.InteractiveShell.run_line_magic()`

.. todo:: Logging TODOs

    - Truncate output if it exceeds a certain threshold.
        - Run **dir(np)** or **dir(pd)** a couple of times and the logs
          become swamped.
    - Possibly change that section under the shebang to also include 3
      double quotes and in the comment add system info like py version, venv,
      conda, any of the 1000000 things you could add.


Roadmap
========

05/18/2019:

Should consider using that ipython_logger_05 as a :class:`logging.FileHandler`
and then configure a globally available :class:`logging.StreamHandler`.

-----------

"""
import logging
import os
import sys
import time
from os import path

from IPython import get_ipython


def ipython_logger_05(shell=None):
    """Saves all commands run in the interactive namespace as valid IPython code.

    .. note:: This is not necessarily valid python code.

    The commands are appended to a file in the directory of the
    profile in :envvar:`$IPYTHONDIR` or fallback ~/.ipython. This file is
    named based on the date.

    Parameters
    -----------
    _ip : |ip|
        Global IPython instance.
        :param shell:
        :type shell:

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
    ipython_logger_05(_ip)
    del ipython_logger_05
