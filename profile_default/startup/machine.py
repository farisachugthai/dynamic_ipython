#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a class for all :mod:`IPython` instances to utilize.

=========
Machine
=========

This class leverages :mod:`prompt_toolkit and a few of it's methods to abstract
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
:mod:`profile_default.startup.20_aliases.py`
    Shows an example use case

"""
import os
from pathlib import Path
import platform
import sys

from IPython import get_ipython
from prompt_toolkit.utils import is_conemu_ansi, is_windows

from profile_default.startup import 05_log

LOGGER = 05_log._setup_logging()


class Platform:
    """Abstract away platform differences.

    Initializing the class now causes issues during IPython startup.
    Glossing over the source for pathlib indicates that there's a class
    Flavour that's created at some point in the `Path.__new__()` func.

    Seemingly going to be more difficult than anticipated to subclass Path.

    After struggling for a while and considering a variety of options,
    including decorating a :ref:`pathlib.Path` subclass with the methods I
    wanted to implement, I realized that as no methods are going to be
    explicitly overridden, I could simply bind the :class:`pathlib.Path()`
    instance directly to :ref:`Platform` during initialization.

    Parameters
    ----------
    shell : |ip|, optional
        Global IPython Instance

    """

    def __init__(self, shell=None, *args, **kwargs):
        """Initialize the platform class."""
        if not shell:
            try:
                shell = get_ipython()
            except Exception as e:
                # is this the right method?
                LOGGER.exception(e)

        if not shell:
            shell = get_ipython()
        self.shell = shell
        self.env = dict(os.environ)
        self.Path = Path

    @classmethod
    def _sys_platform(cls):
        """Return the lower-case value of sys.platform."""
        return sys.platform.lower()

    @classmethod
    def _sys_check(cls):
        """Check OS."""
        return platform.uname().system

    @classmethod
    def is_win(cls):
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
        return self._sys_platform() == 'linux'

    @property
    def env(self):
        self.env = dict(os.environ)
        return self.env

    @env.setter
    def env(self, arg):
        os.environ.set(arg)
