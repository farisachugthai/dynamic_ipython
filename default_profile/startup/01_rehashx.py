#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize exception handlers and run `%rehashx`.

rehashx magic
-------------

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
import cgitb
import code
import logging
import platform
import sys
import threading
import traceback
from os import scandir, listdir
from pathlib import Path
from traceback import format_exc, format_tb
from runpy import run_path

from typing import Any, Callable, Iterable, List, Mapping, Optional, AnyStr
from types import TracebackType

from IPython.core.getipython import get_ipython

logging.basicConfig(level=logging.WARNING)


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


def get_exec_dir() -> AnyStr:
    """Returns IPython's profile_dir.startup_dir. If that can't be determined, return CWD."""
    _ip = get_ipython()
    if _ip is not None:
        exec_dir = _ip.profile_dir.startup_dir
    else:
        exec_dir = "."
    return exec_dir


def safe_run_path(fileobj, logger=None) -> Mapping:
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
    logger = logging.getLogger(name=__name__)
    logger.addHandler(logging.StreamHandler())
    logger.addFilter(logging.Filter())
    logger.setLevel(logging.WARNING)
    for i in scandir(exec_dir):
        if i.name.endswith(".py"):
            try:
                ret.update(safe_run_path(i.name, logger=logger))
            except Exception as e:
                logger.exception(e)
    return ret


def execfile(filename, global_namespace=None, local_namespace=None):
    """Python3 doesn't have this but it'd be nice to have a utility to exec a file at once."""
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


if __name__ == "__main__":
    handled = cgitb.Hook(file=sys.stdout, format="text")
    sys.excepthook = handled

    _ip = get_ipython()

    if _ip is not None:
        _ip.excepthook = handled
        if platform.platform().startswith("Win") and "Dropbox" in listdir("."):
            # yeah it executes everything in the dir but checks for permission incorrectly
            pass
        else:
            rehashx_run()
