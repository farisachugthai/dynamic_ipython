#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==================
Platform Utilities
==================

The Platform class in this module can be easily initialized with:

>>> from default_profile.util.machine import Platform
>>> users_machine = Platform()
>>> users_machine.update_env()
>>> assert users_machine  is not None

.. note::

    Don't name the instance `platform` as that's a module in the standard
    library.


See Also
--------
:mod:`default_profile.startup.20_aliases`
    Shows an example use case

"""
from pathlib import Path
import logging
import os
import platform
import reprlib
import sys

from IPython.core.getipython import get_ipython


class Platform:
    """Abstract away platform differences.

    After toying with the initial implementation, I realized I could simply
    bind the :class:`pathlib.Path()` instance directly to `Platform`
    during initialization.

    This allows for a user to check the `sys.platform` instance, and then
    act in an appropriate manner without knowing what the
    :class:`pathlib.Path` actually initialized to.

    Parameters
    ----------
    shell : |ip|, optional
        Global IPython instance.
    user_env : dict, optional
        Environment variables to add to the instance.

    """
    def __init__(self, shell=None, env=None, **kwargs):
        """Initialize a user specific object.

        Parameters
        ----------
        shell : |ip|, optional
            Global IPython instance.
        env : dict, optional
            User environment variables.

        Attributes
        ----------
        LOGGER : :class:`logging.Logger`
            Class attribute. Logger for the class
        _sys_platform : TODO (type?)
            Value returned by sys.platform

        """
        try:
            self.logger = kwargs["LOGGER"]
        except KeyError:
            self.logger = logging.basicConfig(level=logging.INFO)

        self.shell = shell
        if self.shell is None:
            self.shell = get_ipython()

        if env is None:
            self.env = self.get_env()
        else:
            self.env = env

        self._sys_platform = sys.platform.lower() or _sys_platform
        self._platform_system = platform.system()
        self.Path = Path

    def __repr__(self):
        return "{!r}: {!r}.".format(self.__class__.__name__,
                                    self._sys_platform)

    @property
    def is_windows(self):
        return self._sys_platform.startswith("win")

    @property
    def uname(self):
        return platform.uname().system

    @property
    def is_conemu(self):
        # refactor to self.env.keys().index('ConEmuAnsi')?
        return self.is_windows and os.environ.get("ConEmuANSI", "OFF") == "ON"

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
        return self._sys_platform == "linux"

    @staticmethod
    def get_env():
        """

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
        """Unsure of how to implement this. TODO:"""
        pass

    @property
    def is_powershell(self):
        pass

    @property
    def is_pwsh(self):
        pass


if __name__ == "__main__":
    # put the import in the if main so that we can still doc this without
    # installing it
    from default_profile.util.module_log import stream_logger

    MACHINE_LOGGER = stream_logger(
        logger="default_profile.util.machine",
        msg_format="%(asctime)s : %(levelname)s : %(module)s : %(message)s : ",
        log_level=logging.INFO,
    )

    users_machine = Platform(shell=get_ipython(),
                             LOGGER=MACHINE_LOGGER,
                             env=os.environ.copy())
