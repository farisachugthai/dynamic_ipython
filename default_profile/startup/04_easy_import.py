#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This imports a few utility functions from :mod:`IPython` and imports the python
package neovim is served in.
"""
import sys
from importlib import import_module

from IPython.lib.deepreload import reload as _reload


class DeepReload:
    """Load IPython's `%deepreload` magic.

    Attributes
    ----------
    excludes : set of str, optional
        Modules that won't be reloaded in order to preserve
        :any:`sys.displayhook` and :any:`sys.excepthook`.

    """
    excludes = ('sys', 'os.path', 'builtins', '__main__', 'io', 'numpy',
                'numpy._globals', 'IPython')

    def __init__(self, excludes=None):
        """How do we set an instance attribute with a class attribute?"""
        if excludes == None:
            self.excludes = excludes

    def __repr__(self):
        return '{!r}'.format(repr(self.excludes))

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
        mod = 'pynvim'
    else:
        mod = 'neovim'

    easy_import(mod)
