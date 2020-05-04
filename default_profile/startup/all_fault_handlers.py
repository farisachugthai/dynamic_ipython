#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize exception handlers and run `%rehashx`.

`%rehashx` magic
----------------

This is an incredible little gem that's hugely useful for
making IPython work as a more versatile system shell.

Unfortunately, it executes files in the cwd in an odd manner on Windows,
and believes files on Dropbox should be executed without checking a filetype.

Work in Progress
-----------------

Reorganizing this code to focus on setting up tracers, debuggers and
formatters for exceptions.

The code that's more important than anything should execute regardless
of whether someone has ``pip install``-ed it.
As a result, local imports or any imports not in the standard library
should be discouraged here.

.. tip::
    A possible alternative to get_ipython().showsyntaxerror might
    possibly be :func:`dis.distb`.

"""
import code
import logging
import os
import platform
import sys
import threading
import traceback

from cgitb import Hook
from os import scandir, listdir
from pathlib import Path
from traceback import format_exc, format_tb
from runpy import run_path

from typing import Any, Callable, Iterable, List, Mapping, Optional, Union, AnyStr
from types import TracebackType

from IPython.core.getipython import get_ipython
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.StreamHandler())
logger.addFilter(logging.Filter())
logger.setLevel(logging.WARNING)


def formatted_tb() -> TracebackType:
    """Return a str of the last exception.

    Returns
    -------
    str

    """
    return format_tb(*sys.exc_info())


def last_exc() -> TracebackType:
    """Return `format_exc`."""
    return format_exc()


def rehashx_run() -> None:
    """Add all executables on the user's :envvar:`PATH` into the IPython ns."""
    get_ipython().run_line_magic("rehashx", "")


def get_exec_dir() -> Union[AnyStr, os.PathLike, Path]:
    """Returns IPython's profile_dir.startup_dir. If that can't be determined, return CWD."""
    _ip = get_ipython()
    if _ip is not None:
        exec_dir = _ip.profile_dir.startup_dir
    else:
        exec_dir = "."
    return exec_dir


def safe_run_path(
    fileobj: Union[Path],
    logger: Optional[logging.Logger] = None,
) -> Mapping:
    """Run a file with runpy.run_path and try to catch everything."""
    if logger is None:
        logger = logging.getLogger(name=__name__)
    logger.debug("File to execute is: %s", fileobj)
    try:
        return run_path(fileobj, init_globals=globals(), run_name="rerun_startup")
    except ImportError:
        logger.warning("ImportError for mod: ", sys.last_value)
    except ConnectionResetError:  # happens in windows async loop all the time
        pass
    except OSError as e:
        if hasattr(e, "winerror"):  # same reason
            pass
        else:
            logger.exception(e)
    except Exception as e:  # noqa
        logger.exception(e)
        raise


def rerun_startup():
    """Rerun the files in the startup directory.

    Returns
    -------
    ret : dict
         Namespace of all successful files.

    """
    ret = {}
    exec_dir = get_exec_dir()
    for i in scandir(exec_dir):
        if i.name.endswith(".py"):
            try:
                ret.update(safe_run_path(i.name, logger=logger))
            except Exception as e:
                logger.exception(e)
    return ret


def execfile(filename, global_namespace=None, local_namespace=None):
    """Bring execfile back from python2.

    This function is similar to the `exec` statement, but parses a file
    instead of a string.  It is different from the :keyword:`import` statement in
    that it does not use the module administration --- it reads the file
    unconditionally and does not create a new module.

    The arguments are a file name and two optional dictionaries.  The file is parsed
    and evaluated as a sequence of Python statements (similarly to a module) using
    the *globals* and *locals* dictionaries as global and local namespace. If
    provided, *locals* can be any mapping object.  Remember that at module level,
    globals and locals are the same dictionary. If two separate objects are
    passed as *globals* and *locals*, the code will be executed as if it were
    embedded in a class definition.

    If the *locals* dictionary is omitted it defaults to the *globals* dictionary.
    If both dictionaries are omitted, the expression is executed in the environment
    where :func:`execfile` is called.  The return value is ``None``.

    .. note::

        The default *locals* act as described for function :func:`locals` below:
        modifications to the default *locals* dictionary should not be attempted.  Pass
        an explicit *locals* dictionary if you need to see effects of the code on
        *locals* after function :func:`execfile` returns.  :func:`execfile` cannot be
        used reliably to modify a function's locals.

    """
    if global_namespace is not dict:  # catch both None and any wrong formats
        global_namespace = globals()
    if local_namespace is not dict:  # catch both None and any wrong formats
        local_namespace = locals()
    with open(filename, "rb") as f:
        return exec(
            compile(f.read(), filename, "exec"), global_namespace, local_namespace
        )


def ipy_execfile(f):
    """Run the IPython `%run` -i on a file."""
    get_ipython().run_line_magic("run", "-i", f)


def ipy_execdir(directory):
    """Execute the python files in `directory`.

    The idea was to create a function that actually does what
    the function in this module `execfile` was trying to do.
    Because that `execfile` executes everything in separate namespaces,
    it doesn't get added into the user's `locals`, which is fairly
    pointless for interactive use.

    Parameters
    ----------
    directory : str (os.Pathlike)
        Dir to execute.

    """
    for i in scandir(directory):
        if i.name.endswith("py") or i.name.endswith("ipy"):
            get_ipython().run_line_magic("run", "-i", i.name)


def pyg_highlight(param, **kwargs):
    """Run a string through the pygments highlighter."""
    return pygments.highlight(param, lexer, formatter)


if __name__ == "__main__":
    handled = Hook(file=sys.stdout, format="text")

    lexer = PythonLexer()
    formatter = TerminalTrueColorFormatter()
    # sys.excepthook = pygments.highlight(handled, lexer, formatter)

    _ip = get_ipython()

    if _ip is not None:
        _ip.excepthook = handled
