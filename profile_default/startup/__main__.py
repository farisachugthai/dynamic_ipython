#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the main startup for the IPython startup directory.

==========
__main__
==========


Origin
=======

This definitely came from the IPython team but I need to note where.

Don't remember currently.

07/08/2019

Admittedly this is an odd way of doing this because here's what the get_ipython() call is doing.::

    def get_ipython():
        from IPython.core.interactiveshell import InteractiveShell
        if InteractiveShell.initialized():
            return InteractiveShell.instance()


"""
import logging
import os
import sys

from IPython import get_ipython
# from IPython.core.debugger import BdbQuit_excepthook
from IPython.core.interactiveshell import InteractiveShell
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.utils.path import ensure_dir_exists

from profile_default.util.module_log import stream_logger
log = logging.getLogger(name=__name__)

LOGGER = stream_logger(logger=log)

_ip = InteractiveShell

if _ip.initialized():
    # Running inside IPython

    # Detect if embed shell or not and display a message
    if isinstance(_ip, InteractiveShellEmbed):
        sys.stderr.write("\nYou are currently in an embedded IPython shell,\n"
                         "the configuration will not be loaded.\n\n")
else:
    # Not inside IPython
    # Build a terminal app in order to force ipython to load the configuration
    ipapp = TerminalIPythonApp()
    # Avoid output (banner, prints)
    ipapp.interact = False
    # 07/08/2019: Ensure that we load from the correct spot. IPython will load a different profile if a folder named
    # profile_default is beneath the spot it initializes in. ...aka it will leave log files and a history.sqlite
    # in this repo.

    if sys.argv[1] is None:
        profile_to_load = os.path.expanduser(
            ''.join('~/.ipython/profile_default'))

    if ensure_dir_exists(profile_to_load):
        ipapp.profile_dir = os.path.expanduser('~/.ipython/profile_default')
    else:
        LOGGER.error('%s does not exist' % profile_to_load)

    ipapp.initialize([])
    shell = ipapp.shell