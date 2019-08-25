#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=========
Machine
=========

.. module:: machine
    :synopsis: Create a class for all :mod:`IPython` instances to utilize.

.. highlight:: ipython

This class leverages :mod:`prompt_toolkit` and a few of it's methods to abstract
away differences in operating systems and filesystems.

The class can be easily initialized with:

>>> from profile_default.util.machine import Platform
>>> users_machine = Platform()
>>> env = users_machine.update_env()
>>> assert env is not None

.. note::

    Don't name the instance `platform` as that's a module in the standard
    library.

See Also
--------
:mod:`profile_default.startup.20_aliases`
    Shows an example use case

"""
import doctest
import logging
import os
import platform
import sys
from pathlib import Path

from IPython import get_ipython
from prompt_toolkit.utils import is_conemu_ansi

from profile_default.util import module_log


class Platform:
    """Abstract away platform differences.

    After toying with the initial implementation, I realized I could simply
    bind the :class:`pathlib.Path()` instance directly to `Platform`
    during initialization.

    This allows for a user to check the `sys.platform` instance, and then
    act in an appropriate manner without knowing what the
    :class:`pathlib.Path()` actually initialized to.

    Parameters
    ----------
    shell : |ip|, optional
        Global IPython instance.
    user_env : dict, optional
        Environment variables to add to the instance.

    """
    LOGGER = module_log.stream_logger(
        logger='util.machine.Platform',
        msg_format='%(asctime)s : %(levelname)s : %(lineNo)d : %(message)s : ',
        log_level=logging.INFO
    )

    def __init__(self, shell=None, user_env=None):
        if not shell:
            try:
                self.shell = get_ipython()
            except Exception as e:
                LOGGER.error(e, exc_info=True)

            if shell:
                self.shell = shell

        self.env = self.get_env()
        self._sys_platform = sys.platform.lower()
        self._sys_check = platform.uname().system
        self.is_win = self.is_windows()
        self.is_conemu = self.is_conemu_ansi()
        self.Path = Path

    def __repr__(self):
        return '{!r}: {!r}.'.format(
            self.__class__.__name__, self._sys_platform
        )

    @staticmethod
    def is_windows(self):
        return self._sys_platform.startswith('win')

    @staticmethod
    def is_conemu_ansi(self):
        # refactor to self.env.keys().index('ConEmuAnsi')?
        return self.is_windows(
        ) and os.environ.get('ConEmuANSI', 'OFF') == 'ON'

    @property
    def is_win_vt100(self):
        """True when we are using Windows, but with VT100 esc sequences.

        Import needs to be inline. Windows libraries are not always available.
        """
        from prompt_toolkit.output.windows10 import is_win_vt100_enabled
        return self.is_win and is_win_vt100_enabled()

    @property
    def is_linux(self):
        """True when :func:`sys.platform` returns linux."""
        return self._sys_platform == 'linux'

    def get_env(self):
        """Unsurprisingly stolen from IPython.

        Returns
        --------
        env : dict
            The user's environment variables.

        """
        return os.environ.copy()

    def update_env(self, env=None, **kwargs):
        """Add more arguments to the environment.

        Parameters
        ----------
        env : dict
            Current environment variables.
        kwargs : dict
            Extra arguments to the env.

        """
        if self.env is None:
            env = os.environ.copy()
        return env.update(**kwargs)


class Shell(Platform):
    """Subclass Platform to gain information about the user's shell."""

    @property
    def is_cmd(self):
        pass

    @property
    def is_powershell(self):
        pass

    @property
    def is_pwsh(self):
        pass


if __name__ == "__main__":
    # Modules kept importing this and ending up with 2 loggers and i was confused
    MACHINE_LOGGER = module_log.stream_logger(
        logger='util.machine',
        msg_format='%(asctime)s : %(levelname)s : %(module)s : %(message)s : ',
        log_level=logging.INFO
    )

    # doctest.testmod()
