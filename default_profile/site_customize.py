#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sitecustomize startup script that adds niceties to the interactive interpreter.

This script adds the following things:

- Readline bindings, tab completion, and history (in ~/.history/python,
  which can be disabled by setting NOHIST in the environment)

- Pretty printing of expression output (with Pygments highlighting)

- Pygments highlighting of tracebacks

- Function arguments in repr() for callables

- A source() function that displays the source of an arbitrary object
  (in a pager, with Pygments highlighting)


Cython's site-customize
------------------------
Cython is a compiler. Therefore it is natural that people tend to go
through an edit/compile/test cycle with Cython modules. But my personal
opinion is that one of the deep insights in Python's implementation is
that a language can be compiled (Python modules are compiled to .pyc)
files and hide that compilation process from the end-user so that they
do not have to worry about it. Pyximport does this for Cython modules.
For instance if you write a Cython module called foo.pyx, with
Pyximport you can import it in a regular Python module like this::

    import pyximport; pyximport.install()

"""
import cgitb
import contextlib
import gc
import inspect
import linecache
import logging
import os
import pprint
import re
import shutil
import site
import sys
import threading
import traceback
import types

from inspect import findsource, getmodule, getsource, getsourcefile, getsourcelines
from linecache import cache
from pathlib import Path
from pydoc import pager, safeimport
from typing import Optional, AnyStr

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(name=__name__)

try:
    import pygments
    from pygments.lexers.python import PythonLexer, PythonTracebackLexer
    from pygments.formatters.terminal256 import TerminalTrueColorFormatter
except ImportError:
    pygments = None
    lexer = None
    formatter = None
else:
    lexer = PythonLexer()
    formatter = TerminalTrueColorFormatter()


try:
    import readline
except ImportError:
    readline = None

# pyreadline handles rlcompleter incorrectly so we only import it if we're not
# using pyreadline
try:
    import pyreadline
except ImportError:
    import rlcompleter
else:
    rlcompleter = None


# Globals:
site.enablerlcompleter()
site.ENABLE_USER_SITE = True
site.check_enableusersite()
ENV = os.environ.copy()
PS1 = "\001\033[0;32m\002>>> \001\033[1;37m\002"
PS2 = "\001\033[1;31m\002... \001\033[1;37m\002"


def install_jedi():
    try:
        import jedi
    except ImportError:
        jedi = None
    else:
        from jedi.api import replstartup
    if jedi is not None:
        jedi.settings.auto_import_modules = ["readline", "pygments", "ast"]


def pyg_highlight(*param, outfile=None):
    """Run a string through the pygments highlighter."""
    if pygments is None:
        pprint.pprint(*param)
        return
    return pygments.format(lex(*param, lexer), formatter, outfile)


def _complete(text, state):
    old_complete = readline.get_completer()
    if not text:
        # Insert four spaces for indentation
        return ("    ", None)[state]
    else:
        return old_complete(text, state)


def _pythonrc_enable_readline():
    """Enable readline, tab completion, and history"""
    readline.set_history_length(-1)
    readline.parse_and_bind('"Tab":complete')
    readline.parse_and_bind('"\\C-Space":menu-complete')
    readline.parse_and_bind('"\\C-a":beginning-of-line')
    readline.parse_and_bind('"\\C-b":backward-char')
    readline.parse_and_bind('"\\C-e":end-of-line')
    readline.parse_and_bind('"\\C-f":forward-char')
    readline.parse_and_bind('"\\C-h":backward-delete-char')
    readline.parse_and_bind('"\\C-i":complete')
    readline.parse_and_bind('"\\C-j":accept-line')
    readline.parse_and_bind('"\\C-k":kill-whole-line')
    readline.parse_and_bind('"\\C-l":clear-screen')
    readline.parse_and_bind('"\\C-m":accept-line')
    inputrc = os.environ.get("INPUTRC")
    if inputrc is None:
        inputrc = os.path.exists(os.path.join(os.environ.get("HOME"), "", ".inputrc"))
    if inputrc:
        if hasattr(readline, "read_init_file"):
            readline.read_init_file(inputrc)
    if rlcompleter is not None:
        readline.set_completer(rlcompleter.Completer.complete)


def write_history(history_path: Optional[os.PathLike] = None):
    """If readline was correctly imported, append to the history_path.

    .. currentmodule:: readline

    .. function:: append_history_file(nelements[, filename])

    Append the last *nelements* items of history to a file.  The default filename is
    :file:`~/.history`.  The file must already exist.  This calls
    :c:func:`append_history` in the underlying library.  This function
    only exists if Python was compiled for a version of the library
    that supports it.

    .. versionadded:: 3.5


    .. function:: get_history_length()
                  set_history_length(length)

    Set or return the desired number of lines to save in the history file.
    The :func:`write_history_file` function uses this value to truncate
    the history file, by calling :c:func:`history_truncate_file` in
    the underlying library.  Negative values imply
    unlimited history file size.

    Parameters
    ----------
    history_path : os.PathLike


    """
    if readline is None:
        return
    length = readline.get_current_history_length()
    readline.append_history_file(length, history_path)
    logger.info("Written history to %s" % history_path)


def _pythonrc_enable_history():
    """Register readline's history functions with atexit."""
    if readline is None:
        return
    history_path = Path("~/.python_history").expanduser()
    if not history_path.exists():
        try:
            hist_path.touch()
        except PermissionError:
            raise
        except OSError:
            print("Error while trying to create the history file.")


def pphighlight(o, *a, **kw):
    """Lex a `pprint.pformat`\'ted str, then run it through `pyg_highlight`."""
    s = pprint.pformat(o, *a, **kw)
    try:
        sys.stdout.write(pyg_highlight(s))
    except UnicodeError:
        sys.stdout.write(s)
        sys.stdout.write("\n")


def get_height() -> os.terminal_size:
    return shutil.get_terminal_size()


def get_width() -> AnyStr:
    return shutil.get_terminal_size()[1]


def excepthook_(exctype, value, traceback):
    """Prints exceptions to sys.stderr and colorizes them.

    Notes
    -----
    traceback.format_exception() isn't used because it's
    inconsistent with the built-in formatter
    """
    import traceback

    ret = pyg_highlight(traceback.print_exception(etype, value, tb))

    try:
        stderror = sys.stderr.getvalue()
        pyg_highlight(stderror)
    except:  # noqa
        # oops
        sys.__excepthook__(exctype, value, tb)
        print(sys.stderr.getvalue())
    finally:
        sys.exc_info = (None, None, None)
        gc.collect()


def format_callable(value):
    """Use either inspect.getfullargspec or getargpspec to format a callable."""
    if hasattr(inspect, "getfullargspec"):
        getargspec = inspect.getfullargspec
    else:
        getargspec = inspect.getargspec

    reprstr = repr(value)

    if inspect.isfunction(value):
        parts = reprstr.split(" ")
        parts[1] += getargspec(*getargspec(value))
        reprstr = " ".join(parts)
    elif inspect.ismethod(value):
        parts = reprstr[:-1].split(" ")
        parts[2] += inspect.formatargspec(*getargspec(value))
        reprstr = " ".join(parts) + ">"
    return reprstr


def pprinthook(value=None, *args, **kwargs):
    """Pretty print an object to sys.stdout.

    Replacement for ``print`` that special-cases dicts and iterables.

    - Dictionaries are printed one line per key-value pair, with key and value colon-separated.

    - Iterables (excluding strings) are printed one line per item

    - Everything else is delegated to `print`. An optional heading may be added
      for non-iterables with ``__doc__`` defined.

    """
    if value is None:
        return
    from typing import Iterable

    if len(args) != 1:
        print(*args, **kwargs)
        return
    x = args[0]
    if isinstance(x, dict):
        for k, v in x.items():
            print(f"{k}:", v, **kwargs)
    elif isinstance(x, Iterable) and not isinstance(x, str):
        for i in x:
            print(i, **kwargs)
    else:
        if getattr(value, "__doc__", None):
            import pydoc

            sys.stdout.write("\n" + str(pydoc.getdoc(value)) + "\n")
            return
        print(x, **kwargs)


def get_help_types():
    import types

    help_types = [
        types.BuiltinFunctionType,
        types.BuiltinMethodType,
        types.FunctionType,
        types.MethodType,
        types.ModuleType,
        type,
        # method_descriptor
        type(list.remove),
    ]
    if hasattr(types, "UnboundMethodType"):
        help_types.append(types.UnboundMethodType)
    help_types = tuple(help_types)
    return help_types


def pf(obj):
    """Display the source code of an object.

    Applies syntax highlighting if Pygments is available.
    """
    try:
        # Check to see if the object is defined in a shared library, which
        # findsource() doesn't do properly (see issue4050)
        if not getsourcefile(obj):
            raise TypeError
        s = getsource(obj)
    except TypeError:
        logger.exception(
            "Source code unavailable (maybe it's part of " "a C extension?)\n"
        )
        return

    # Detect the module's file encoding. We could use
    # tokenize.detect_encoding(), but it's only available in Python 3.
    enc = "ascii"
    for line in findsource(getmodule(obj))[0][:2]:
        m = re.search(r"coding[:=]\s*([-\w.]+)", line)
        if m:
            enc = m.group(1)
    if hasattr(s, "decode"):
        try:
            s = s.decode(enc, "replace")
        except LookupError:
            s = s.decode("ascii", "replace")

    # Display the source code in the pager, and try to convince less not to
    # escape color control codes.
    has_lessopts = "LESS" in os.environ
    lessopts = os.environ.get("LESS", "")
    try:
        os.environ["LESS"] = lessopts + " -R"
        if hasattr(s, "decode"):
            pager(s.encode(sys.stdout.encoding, "replace"))
        else:
            pager(s)
    finally:
        if has_lessopts:
            os.environ["LESS"] = lessopts
        else:
            os.environ.pop("LESS", None)


def ps(obj):
    return pprint.pprint(getsourcelines(obj))


@contextlib.contextmanager
def as_cwd(new_dir, *args, **kwargs):
    old_cwd = Path.cwd()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(old_dir)


def rerun_startup():
    try:
        if readline is not None:
            _pythonrc_enable_readline()
        _pythonrc_enable_history()
        # sys.displayhook = pprinthook
    except Exception as e:
        print(e)


if __name__ == "__main__":
    if sys.stdout.isatty():
        sys.ps1 = "\001\033[0;32m\002>>> \001\033[1;37m\002"
        sys.ps2 = "\001\033[1;31m\002... \001\033[1;37m\002"
        rerun_startup()
        install_jedi()
        cgitb.enable(format="text")
        sys.excepthook = excepthook_
