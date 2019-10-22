#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. _machine:

==================
Platform Utilities
==================

The Platform class in this module can be easily initialized with:

>>> from default_profile.util.machine import Platform
>>> users_machine = Platform()
>>> env = users_machine.update_env()
>>> assert env is not None

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
from os import _Environ
import platform
import reprlib
import sys

from IPython import get_ipython

from default_profile.util import module_log


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

    LOGGER = module_log.stream_logger(
        logger='util.machine.Platform',
        msg_format='%(asctime)s : %(levelname)s : %(lineNo)d : %(message)s : ',
        log_level=logging.INFO)

    def __init__(self, shell=None, env=None, LOGGER=None):
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
        if not shell:
            try:
                self.shell = get_ipython()
            except Exception as e:
                LOGGER.error(e, exc_info=True)

            if shell:
                self.shell = shell

        if env is None:
            self.env = self.get_env()
        else:
            self.env = env

        self._sys_platform = sys.platform.lower()
        self._sys_check = platform.uname().system
        self.is_win = self.is_windows()
        self.is_conemu = self.is_conemu_ansi()
        self.Path = Path

    def __repr__(self):
        return '{!r}: {!r}.'.format(self.__class__.__name__,
                                    self._sys_platform)

    def is_windows(self):
        return self._sys_platform.startswith('win')

    def is_conemu_ansi(self):
        # refactor to self.env.keys().index('ConEmuAnsi')?
        return self.is_windows() and os.environ.get('ConEmuANSI',
                                                    'OFF') == 'ON'

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

    @staticmethod
    def get_env():
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
        """Unsure of how to implement this. TODO:"""
        pass

    @property
    def is_powershell(self):
        pass

    @property
    def is_pwsh(self):
        pass


class DisplayAliases(reprlib.Repr):
    """Because I literally lose the output from other commands I wanted to see because of my aliases.

    Examples
    --------
    ::

        In[54]: DisplayAliases()
        Out[54]: {'..': 'cd ..', '...': 'cd ../..', 'copy': 'copy %s %s', 'cp': 'copy %s %s', ...}

    """
    def __init__(self, shell=None, user_aliases=None):
        self.shell = shell or get_ipython()
        self.maxdict = 20
        self.user_aliases = user_aliases or self.shell.alias_manager.user_aliases
        super().__init__()

    @property
    def _dict_user_aliases(self):
        return self.flatten()

    def flatten(self):
        dict_aliases = {}
        if len(self.user_aliases) == 0:
            return
        for idx, alias_tuple in enumerate(self.user_aliases):
            dict_aliases[self.user_aliases[idx][0]] = self.user_aliases[idx][1]
            return dict_aliases

    def __repr__(self):
        """TODO"""
        return self.repr_dict(self._dict_user_aliases, 50)


if __name__ == "__main__":
    # Modules kept importing this and ending up with 2 loggers and i was confused
    MACHINE_LOGGER = module_log.stream_logger(
        logger='util.machine',
        msg_format='%(asctime)s : %(levelname)s : %(module)s : %(message)s : ',
        log_level=logging.INFO)

    # Not useful as i have it here but it's a good reference for the user env
    Environ = _Environ()
    Platform()
