#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the main startup for the IPython startup directory.

==========
__main__
==========

.. highlight:: ipython

.. Can we put a module directive here? Would it fuck something up to see
.. module\:\: main here?


07/08/2019:

    def get_ipython():
        from IPython.core.interactiveshell import InteractiveShell
        if InteractiveShell.initialized():
            return InteractiveShell.instance()


"""
import errno
import logging
import os
from pathlib import Path
import sys  # unresolved import sys??

from IPython import get_ipython
# from IPython.core.debugger import BdbQuit_excepthook
from IPython.core.interactiveshell import InteractiveShell
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.embed import InteractiveShellEmbed

from profile_default.util.module_log import stream_logger

log = logging.getLogger(name='profile_default.startup.__main__')

LOGGER = stream_logger(logger=log)

class Dynamic:
    """Organize personal configuration code into one class.

    This module was created to allow users to override what they need as
    necessary.
    """
    canary = InteractiveShell

    def __init__(self):
        if self.canary.initialized():
            # Running inside IPython

            # Detect if embed shell or not and display a message
            if isinstance(self.canary, InteractiveShellEmbed):
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

    @staticmethod
    def ensure_dir_exists(path, mode=0o755):
        """Ensure that a directory exists.

        If it doesn't exist, try to create it and protect against a race
        condition if another process is doing the same.

        The default permissions are :data:`0o755`, which differ from
        :func:`os.makedirs()` default of :data:`0o777`.

        Parameters
        ----------
        todo

        Returns
        -------
        None
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path, mode=mode)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        elif not os.path.isdir(path):
            raise IOError("%r exists but is not a directory" % path)

    def initialize_profile(self):
        """Initialize the profile but sidestep the IPython.core.ProfileDir().

        The class searches for directories named profile_default and if found
        uses that as a profile which I dislike.
        """
        profile_to_load = Path('~/.ipython/profile_default')

        try:
            self.ensure_dir_exists(profile_to_load)
        except OSError as e:
            LOGGER.error(e)
        else:
            self.canary.profile_dir = os.path.expanduser(
                    '~/.ipython/profile_default'
                )

            # kinda lost track of why this module exists.
#     def begin_eventloop(self, ipapp=None):
#         try:
#             ipapp.initialize([])
#         except AttributeError as e:
#             LOGGER.error(e)


def main():
    dynamically = Dynamic()
    dynamically.initialize_profile()
    # dynamically.begin_eventloop(dynamically.canary)


main()
