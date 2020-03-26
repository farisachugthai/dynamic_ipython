#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import logging
import os
import platform
import reprlib
import sys

from IPython.core.getipython import get_ipython


class Platform:

    def __init__(self, shell=None, env=None, **kwargs):
        try:
            self.logger = kwargs["LOGGER"]
        except KeyError:
            logging.basicConfig(level=logging.INFO)

        self.shell = shell if shell is not None else get_ipython()

        self.env = env if env is not None else self.get_env()

        self._sys_platform = sys.platform.lower() or _sys_platform
        self._platform_system = platform.system()
        self.Path = Path

    def __repr__(self):
        return "{!r}: {!r}.".format(self.__class__.__name__, self._sys_platform)

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
        # noinspection PyProtectedMember
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

    users_machine = Platform(
        shell=get_ipython(), LOGGER=MACHINE_LOGGER, env=os.environ.copy()
    )
