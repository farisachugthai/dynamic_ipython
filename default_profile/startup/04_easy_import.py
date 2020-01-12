#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This imports a few utility functions from :mod:`IPython` and imports the python
package neovim is served in.
"""
from importlib import import_module
import io
from io import RawIOBase, BufferedRWPair, BufferedIOBase  # noqa
import logging
from pprint import pprint
from reprlib import Repr
import subprocess
import sys
import tempfile
from textwrap import dedent
import traceback

from IPython.lib.deepreload import reload as _reload
from IPython.core.error import TryNext
from IPython.core.hooks import CommandChainDispatcher  # noqa
from IPython.core.getipython import get_ipython
from IPython.core.magics.execution import ExecutionMagics, _format_time
from IPython.utils.text import SList  # noqa
from traitlets.config import Configurable

from default_profile.startup import STARTUP_LOGGER


class NvimHook(Configurable):
    """todo: Doesnt work.

    Might need to subclass and override
    :class:`IPython.core.hooks.CommandChainDispatcher`.
    """

    def __init__(self, fname=None):
        """Specify the editor arguments. None are required."""
        self.fname = fname
        self.shell = get_ipython()
        super().__init__(parent=self.shell)

    def __repr__(self):
        return "".join(self.__class__.__name__)

    def __str__(self):
        return "Nvim Hook: {}".format(self.fname)

    def nvim_quickfix_file(self, *, fname=None, lineno=None, columnno=None, m=None):
        """The hook.

        Accepts positional parameters to specify filename,
        linenumber, column number and something else?
        """
        if self.fname is None:
            self.fname = tempfile.NamedTemporaryFile()
        if self.run_nvim():
            raise TryNext

    def run_nvim(self):
        """I thought of a clever way to return a nonzero exit code and have it return and raise a TryNext :D"""
        try:
            retval = subprocess.check_call(
                ["nvim", "-c", "set errorformat=%f:%l:%c:%m", "-q", self.fname]
            )
        except subprocess.CalledProcessError:
            pass
        return retval


class IOStream(RawIOBase):
    """Try to rewrite IPythons IPython.utils.io.IOStream.

    Did a little bit but I'd imagine it's gonna need flush methods. Let's
    try subclassing RawIOBase.
    """

    def __init__(self, stream=None, *args, **kwargs):
        self.stream = stream
        if self.stream is None:
            self.stream = io.StringIO()
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "<{}:> --- Stream is currently {}".format(
            repr(self.__class__.__name__), repr(self.stream)
        )

    def __str__(self):
        return "{}\n{}".format(self.__class__.__name__, str(self.stream))

    def write(self, message):
        """Flush streams after any writes."""
        try:
            self.stream.write(message)
        except (AttributeError, TypeError) as e:
            traceback.format_exception(e)
            raise
        finally:
            sys.stdout.flush()
            sys.stderr.flush()

    def read(self):
        try:
            message = self.stream.read()
        except (AttributeError, TypeError) as e:
            traceback.format_exception(e)
            raise
        finally:
            sys.stdout.flush()
            sys.stderr.flush()

        return message


class DeepReload:
    """Load IPython's `%deepreload` magic.

    Attributes
    ----------
    excludes : set of str, optional
        Modules that won't be reloaded in order to preserve
        :any:`sys.displayhook` and :any:`sys.excepthook`.

    """

    excludes = (
        "sys",
        "os.path",
        "builtins",
        "__main__",
        "io",
        "numpy",
        "numpy._globals",
        "IPython",
    )

    def __init__(self, shell, excludes=None):
        if excludes is None:
            self.excludes = excludes
        self.shell = shell

    def __repr__(self):
        return "{!r}".format(Repr.repr(self.excludes))

    def __call__(self):
        self.shell.run_cell(self.dreload(self.excludes))

    def reload(self, *args, **kwargs):
        """Return :func:`IPython.lib.deepreload.dreload`. """
        return _reload(*args, **kwargs)

    def dreload(self, mod, extra_excludes=None):
        """Import IPython's `%deepreload` magic.

        This function exists to modify the ``excludes`` set.

        Parameters
        ----------
        mod : mod
            Module to reload
        extra_excludes : set of str, optional
            Extra modules to exclude from `IPython.lib.deepreload.dreload`.

        Returns
        -------
        set of modules
            Modules that were *excluded* from being erased from the namespace.

        """
        if extra_excludes is not None:
            return _reload(mod, self.excludes + set(extra_excludes))
        else:
            return _reload(mod, self.excludes)


def easy_import(mod):
    """Import a module.

    Utilizes :func:`importlib.import_module()` from :mod:`importlib` so that
    any valid alphanumeric string can be passed without crashing the
    interpreter.

    .. caution::

        Raising :exc:`ImportError` not :exc:`ModuleNotFoundError`
        may render the try/catch useless on python3.7>=.

    Parameters
    ----------
    mod : str
       A module to import.

    Returns
    -------
    ret_mod : mod
        Imported module. Specifically used for neovim in this instance
        but can be interactively used for any module the user needs to import.

    """
    try:
        return import_module(mod)
    except ImportError:
        msg = dedent(
            """
        ************************************************************
        {} import failed. Only ignore this if you plan on going
        the entire session without using it!!
        ************************************************************
        """.format(
                mod
            )
        )


if __name__ == "__main__":
    if sys.version_info > (3, 5):
        mod = "pynvim"
    else:
        mod = "neovim"

    easy_import(mod)
