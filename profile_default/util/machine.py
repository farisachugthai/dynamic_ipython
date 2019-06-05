#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a class for all :mod:`IPython` instances to utilize.

=========
Machine
=========

This class leverages :mod:`prompt_toolkit and a few of it's methods to abstract
away differences in operating systems and filesystems.

The class can be easily initialized with::

    >>> from profile_default.util.machine import Platform
    >>> machine = Platform()
    >>> assert machine.env

.. i ran a doctest and got the following...what does a negative number mean?
.. Testing started at 11:37 PM ...
.. C:\Users\faris\Anaconda3\envs\dynamic\python.exe C:\Users\faris\AppData\Local\JetBrains\Toolbox\apps\PyCharm-P\ch-0\191.7479.10\helpers\pycharm\docrunner.py C:/Users/faris/projects/dynamic_ipython/profile_default/util/machine.py
.. C:\Users\faris\AppData\Local\JetBrains\Toolbox\apps\PyCharm-P\ch-0\191.7479.10\helpers\pycharm\docrunner.py:1: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
.. import imp
.. Process finished with exit code -1073741571 (0xC00000FD)

.. note::

    Don't name the instance ``platform`` as that's a module in the standard
    library.

See Also
--------
:mod:`profile_default.startup.20_aliases`
    Shows an example use case

"""
import os
from pathlib import Path
import platform
import sys

from IPython import get_ipython
from prompt_toolkit.utils import is_conemu_ansi, is_windows

from profile_default.util import logger

LOGGER = logger._setup_logging()


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

        # so let's leave this commented out until we figure out...init param or property
        # self.env = dict(os.environ)
        self._sys_platform = sys.platform.lower()
        self._sys_check = platform.uname().system
        self.is_win = is_windows()
        self.is_conemu = is_conemu_ansi()
        self.Path = Path

    @property
    def is_win_vt100(self):
        """True when we are using Windows, but with VT100 esc sequences.

        Import needs to be inline. Windows libraries are not always available.
        """
        from prompt_toolkit.output.windows10 import is_win_vt100_enabled
        return self.is_win() and is_win_vt100_enabled()

    @property
    def is_linux(self):
        """True when :func:`sys.platform` returns linux."""
        return self._sys_platform == 'linux'

    @property
    def env(self):
        self.env = dict(os.environ)
        return self.env

    @env.setter
    def env(self, arg):
        return self.env.putenv(arg)
