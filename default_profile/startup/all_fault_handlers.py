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
import inspect
import logging
import os
import platform
import sys
import threading
import traceback

from cgitb import Hook
from contextlib import contextmanager
from os import scandir, listdir
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from traceback import format_exc, format_tb
from runpy import run_path
from typing import Any, Callable, Iterable, List, Mapping, Optional, Union, AnyStr, Dict
from types import TracebackType

from IPython.core.getipython import get_ipython
from IPython.terminal.prompts import RichPromptDisplayHook
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(name=__name__)


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


def rehashx_run():
    """Add all executables on the user's :envvar:`PATH` into the IPython ns."""
    get_ipython().run_line_magic("rehashx", "")


def find_exec_dir() -> Union[AnyStr, os.PathLike]:
    """Returns IPython's profile_dir.startup_dir. If that can't be determined, return CWD."""
    _ip = get_ipython()
    if _ip is not None:
        exec_dir = _ip.profile_dir.startup_dir
    else:
        exec_dir = "."
    return exec_dir


def safe_run_path(
    fileobj: Union[AnyStr, os.PathLike],
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


def rerun_startup() -> Dict:
    """Rerun the files in the startup directory.

    Returns
    -------
    ret : dict
         Namespace of all successful files.

    """
    ret = {}
    exec_dir = find_exec_dir()
    for i in scandir(exec_dir):
        if i.name.endswith(".py"):
            try:
                ret.update(safe_run_path(i.name, logger=logger))
            except Exception as e:
                logger.exception(e)
    return ret


def execfile(filename: Union[AnyStr, os.PathLike],
        global_namespace: Optional[Mapping]=None,
        local_namespace: Optional[Mapping]=None):
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


def ipy_execfile(f: Union[AnyStr, os.PathLike]):
    """Run the IPython `%run` -i on a file."""
    get_ipython().run_line_magic("run", "-i", f)


def ipy_execdir(directory: Union[AnyStr, os.PathLike]):
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


def pyg_highlight(param: Any, **kwargs):
    """Run a string through the pygments highlighter."""
    return pygments.highlight(param, lexer, formatter)


@contextmanager
def tempdir():
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.

    Upon exiting the context, the directory and everything contained
    in it are removed.

    Examples
    --------
    >>> import os
    >>> with tempdir() as tmpdir:
    ...     fname = os.path.join(tmpdir, 'example_file.txt')
    ...     with open(fname, 'wt') as fobj:
    ...         _ = fobj.write('a string\\n')
    >>> os.path.exists(tmpdir)
    False

    """
    d = mkdtemp()
    yield d
    rmtree(d)


@contextmanager
def in_tempdir():
    ''' Create, return, and change directory to a temporary directory

    Examples
    --------
    >>> import os
    >>> my_cwd = os.getcwd()
    >>> with in_tempdir() as tmpdir:
    ...     _ = open('test.txt', 'wt').write('some text')
    ...     assert os.path.isfile('test.txt')
    ...     assert os.path.isfile(os.path.join(tmpdir, 'test.txt'))
    >>> os.path.exists(tmpdir)
    False
    >>> os.getcwd() == my_cwd
    True
    '''
    pwd = os.getcwd()
    d = mkdtemp()
    os.chdir(d)
    yield d
    os.chdir(pwd)
    rmtree(d)


@contextmanager
def in_dir(dir: Union[AnyStr, os.PathLike]):
    """ Change directory to given directory for duration of `with` block.

    .. testsetup::

        from default_profile.startupm.all_fault_handlers import in_tempdir, in_dir

    Useful when you want to use `in_tempdir` for the final test, but
    you are still debugging.  For example, you may want to do this in the end.::

    >>> with in_tempdir() as tmpdir:
    ...     # do something complicated which might break
    ...     pass

    But indeed the complicated thing does break, and meanwhile the
    ``in_tempdir`` context manager wiped out the directory with the
    temporary files that you wanted for debugging.  So, while debugging, you
    replace with something like.::

    >>> with in_dir() as tmpdir: # Use working directory by default
    ...     # do something complicated which might break
    ...     pass

    You can then look at the temporary file outputs to debug what is happening,
    fix, and finally replace ``in_dir` with `in_tempdir` again.

    """
    cwd = os.getcwd()
    if dir is None:
        yield cwd
        return
    os.chdir(dir)
    yield dir
    os.chdir(cwd)

if __name__ == "__main__":
    handled = Hook(file=sys.stdout, format="text")

    lexer = PythonLexer()
    formatter = TerminalTrueColorFormatter()
    # sys.excepthook = pygments.highlight(handled, lexer, formatter)

    _ip = get_ipython()

    if _ip is not None:
        _ip.excepthook = handled
