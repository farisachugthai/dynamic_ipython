#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO: Check out conda API both the conda package and conda_api repo"""
import shlex
import sys
from subprocess import Popen, PIPE

from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magics.packaging import (CONDA_ENV_FLAGS, CONDA_YES_FLAGS,
                                           CONDA_COMMANDS_REQUIRING_YES,
                                           CONDA_COMMANDS_REQUIRING_PREFIX,
                                           PackagingMagics)


@magics_class
class PackagingMagics(Magics):
    """Override the PackagingMagic."""

    @property
    def conda_path(self):
        """Is this a thing? Method decorators in magics I mean.

        Also. Property or classmethod?
        """
        return shutil.which('conda')

    @property
    def stdin_disabled(self):
        return getattr(self.shell, kernel, None)

    @line_magic
    def conda(self, line):
        """First do a shutil check.

        Parameters
        ----------
        line : str
            remainder of line

        Raises
        ------
        :exc:`NotImplementedError`

        """
        if self.conda_path is None:
            raise NotImplementedError('conda not installed or on $PATH envvar')

        conda, *cmd = sys.argv

        if self.stdin_disabled is not None:
            # hang on this doesn't seem like a good idea.
            # cmd.append(self.non_interactive_parameters(cmd))
            # TODO
            raise NotImplementedError

        # tbf i still question if that's a good way of checking interactivity
        try:
            if isinstance(self.shell, TerminalInteractiveShell):
                return subprocess.run([conda, *args])
        except AttributeError:
            raise NotImplementedError


def load_ipython_extension(ip):
    """TODO: Docstring for load_ipython_extension.

    Parameters
    ----------
    arg1 : TODO

    Returns
    -------
    TODO

    """
    ip.register_magic(PackagingMagics)
    ip.register_magic_function(PackagingMagics().conda)

