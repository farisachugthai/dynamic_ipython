#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the main startup for the IPython startup directory.

==========
__main__
==========

.. highlight:: ipython

07/08/2019

This module executes a check that's similar in nature to what
an :func:`IPython.get_ipython()` call is doing.::

    def get_ipython():
        from IPython.core.interactiveshell import InteractiveShell
        if InteractiveShell.initialized():
            return InteractiveShell.instance()


"""
import errno
import logging
import os
import sys  # unresolved import sys??
from pathlib import Path

import traitlets
from traitlets.config import Configurable
from IPython import get_ipython
# from IPython.core.debugger import BdbQuit_excepthook
from IPython.core.interactiveshell import InteractiveShell

# from IPython.terminal.debugger import com
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.ipapp import TerminalIPythonApp


class Dynamic(Configurable):
    """Organize personal configuration code into one class.

    This module was created to allow users to override what they need as
    necessary.
    """

    def __init__(self, canary, *args, **kwargs):
        """Initialize our own version of ipython."""
        self.canary = canary
        super().__init__(*args, **kwargs)

    def initialize(self):
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
                    raise IOError(e)
        elif not os.path.isdir(path):
            raise IOError("%r exists but is not a directory" % path)

    def initialize_profile(self):
        """Initialize the profile but sidestep the IPython.core.ProfileDir().

        The class searches for directories named default_profile and if found
        uses that as a profile which I dislike.
        """
        profile_to_load = Path('~/.ipython/default_profile')

        try:
            self.ensure_dir_exists(profile_to_load)
        except OSError as e:
            print(e)
        else:
            self.canary.profile_dir = os.path.expanduser(
                '~/.ipython/default_profile'
            )
