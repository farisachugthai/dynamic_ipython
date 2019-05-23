#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a class for all :mod:`IPython` instances to utilize.

This class leverages Prompt Toolkit and a few of it's methods to abstract
away differences in operating systems and filesystems.

The class can be easily initialized with::

    >>> from profile_default.startup.machine import Platform
    >>> machine = Platform()
    >>> assert machine.env

.. note::

    Don't name the instance ``platform`` as that's a module in the standard
    library.

See Also
--------
:mod:`20_aliases.py`
    Shows an example use case

"""
import os
import platform
import sys

from prompt_toolkit.utils import is_conemu_ansi, is_windows


class Platform:
    """Abstract away platform differences."""

    def __init__(self, shell=None):
        """Initialize the platform class."""
        self.shell = shell
        self.env = dict(os.environ)
        self._sys_platform = sys.platform.lower()
        self._sys_check = platform.uname().system

    @property
    def is_win(self):
        """True when we are using Windows.

        Only checks that the return value starts with 'win' so *win32* and
        *win64* both work.
        """
        return is_windows()

    @classmethod
    def is_conemu(cls):
        """True when the ConEmu Windows console is used. Thanks John."""
        return is_conemu_ansi()

    def is_win_vt100(self):
        """True when we are using Windows, but with VT100 esc sequences.

        Import needs to be inline. Windows libraries are not always available.
        """
        from prompt_toolkit.output.windows10 import is_win_vt100_enabled
        return self.is_win() and is_win_vt100_enabled()

    def is_linux(self):
        """True when :func:`sys.platform` returns linux."""
        return self._sys_platform == 'linux'
