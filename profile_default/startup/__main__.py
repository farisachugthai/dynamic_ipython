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
from pathlib import Path
import sys  # unresolved import sys??

from IPython import get_ipython
# from IPython.core.debugger import BdbQuit_excepthook
from IPython.core.interactiveshell import InteractiveShell
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.utils.path import ensure_dir_exists

from profile_default.util.module_log import stream_logger

log = logging.getLogger(name='profile_default.startup.__main__')

LOGGER = stream_logger(logger=log)

class Dynamic:
    """Let's organize this free flowing code into one class so we can allow users to override what they need as necessary."""
    canary = InteractiveShell

    def __init__(self):
        if canary.initialized():
            # Running inside IPython

            # Detect if embed shell or not and display a message
            if isinstance(canary, InteractiveShellEmbed):
                sys.stderr.write(
                    "\nYou are currently in an embedded IPython shell,\n"
                    "the configuration will not be loaded.\n\n"
                )
        else:
            # Not inside IPython
            # Build a terminal app in order to force ipython to load the configuration
            ipapp = TerminalIPythonApp()
            # Avoid output (banner, prints)
            ipapp.interact = False
            # 07/08/2019: Ensure that we load from the correct spot. IPython will load a different profile if a folder named
            # profile_default is beneath the spot it initializes in. ...aka it will leave log files and a history.sqlite
            # in this repo.

    def initialize_profile(self):
        profile_to_load = Path('~/.ipython/profile_default')

        if ensure_dir_exists(profile_to_load):
            ipapp.profile_dir = os.path.expanduser('~/.ipython/profile_default')
        else:
            LOGGER.error('%s does not exist' % profile_to_load)

    def begin_eventloop(self, ipapp=None):
        ipapp.initialize([])
        shell = ipapp.shell


def main():
    dynamically = Dynamic()
    dynamically.initialize_profile()
    dynamically.begin_eventloop()


main()