#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This imports a few utility functions from :mod:`IPython` and imports the python
package neovim is served in.
"""
from importlib import import_module
import io
import logging
import subprocess
import sys
import tempfile

from IPython.lib.deepreload import reload as _reload
from IPython.core.error import TryNext
from IPython import get_ipython

logging.basicConfig(level=logging.WARN)


class NvimHook:
    """todo: Doesnt work.

    Might need to subclass and override
    :class:`IPython.core.hooks.CommandChainDispatcher`.
    """

    def __init__(self, fname=None):
        """Specify the editor arguments. None are required."""
        self.fname = fname
        self.shell = get_ipython()

    def __repr__(self):
        return ''.join(self.__class__.__name__)

    def __str__(self):
        return 'Nvim Hook: {}'.format(self.fname)

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
            retval = subprocess.check_call(['nvim', '-c', 'set errorformat=%f:%l:%c:%m', '-q', self.fname])
        except subprocess.CalledProcessError:
            pass
        return retval


class IOStream(io.TextIOBase):
    """Try to rewrite IPythons IPython.utils.io.IOStream."""

    def __init__(self, stream, fallback=None):
        if fallback is not None:
            self.stream = fallback
        else:
            self.stream = stream

    def __repr__(self):
        return ''.format(self.__class__.__name__)

    def __str__(self):
        return ''.join(self.__class__.__name__, str(self.stream))

    def write(self, message):
        self.stream.write(message)

    def read(self):
        """Did a smoke test and this is the only method not working.

        >>> s = IOStream(sys.stdout)
        >>> s.write('foo')
        foo

        Worked but s.read() raises as it expect a str,
        bytes or pathlike.
        sys.sydout is an _io.TextWrapper. Hm.
        """
        with open(self.stream, 'rt') as f:
            return f.read()


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
        return "{!r}".format(repr(self.excludes))

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
        Imported module. Specifically used for neovim in this instance but can
        be interactively used for any module the user needs to import.

    Raises
    ------
    :exc:`ImportError`
        If the module isn't imported.

    """
    try:
        return import_module(mod)
    except ImportError:
        print("************************************************************")
        print("{} import failed. Only ignore this if you plan on going".format(mod))
        print(" the entire session without using it")
        print("************************************************************")


if __name__ == "__main__":
    if sys.version_info > (3, 5):
        mod = "pynvim"
    else:
        mod = "neovim"

    easy_import(mod)

    # _ip = get_ipython()
    # if _ip.editor == 'nvim':
    #     _ip.set_hook('editor', NvimHook().nvim_quickfix_file, priority=99)
    # else:
    #     logging.warning('$EDITOR not set. IPython hook not set.')

    # if logging.getLevelName(logging.INFO):
    #     logging.info('The editor hooks are as follows %s: ', _ip.hooks['editor'].__str__())
