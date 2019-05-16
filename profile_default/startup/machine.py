#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a class for all :mod:`IPython` instances to utilize.

This class leverages Prompt Toolkit and a few of it's methods to abstract
away differences in operating systems and filesystems.

"""
import sys

from prompt_toolkit.utils import is_conemu_ansi, is_windows


class Platform:
    """Abstract away platform differences."""

    @classmethod
    def _sys_platform(self):
        """Return the value of sys.platform."""
        return sys.platform

    def is_win(self):
        """True when we are using Windows.

        Only checks that the return value starts with 'win' so *win32* and
        *win64* both work.
        """
        return self.is_windows()

    def is_win_vt100(self):
        """True when we are using Windows, but with VT100 esc sequences.

        Import needs to be inline. Windows libraries are not always available.
        """
        from prompt_toolkit.output.windows10 import is_win_vt100_enabled
        return self.is_windows() and is_win_vt100_enabled()

    @classmethod
    def is_conemu(self):
        """True when the ConEmu Windows console is used. Thanks John."""
        return is_conemu_ansi()

    def is_linux(self):
        """True when :func:`sys.platform` returns Linux."""
        return self._sys_platform() == 'Linux'
