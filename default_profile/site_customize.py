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
import atexit
import cgitb
import inspect
import linecache
import logging
import os
import pprint
import pydoc
import re
import shutil
import site
import sys
import types

from inspect import findsource, getmodule, getsource, getsourcefile
from io import StringIO
from linecache import cache
from pathlib import Path
from pydoc import pager, safeimport

logging.basicConfig(level=logging.WARNING)

parso = safeimport('parso')

try:
    import pygments
    from pygments.lexers.python import PythonLexer, PythonTracebackLexer
    from pygments.formatters.terminal256 import TerminalTrueColorFormatter
except ImportError:
    pass

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

try:
    import jedi
except ImportError:
    jedi = None
else:
    from jedi.api import replstartup

# Globals: {{{
site.enablerlcompleter()
site.ENABLE_USER_SITE = True
site.check_enableusersite()

lexer = PythonLexer()
formatter = TerminalTrueColorFormatter()


# }}}


def pyg_highlight(param, **kwargs):
    """Run a string through the pygments highlighter."""
    return pygments.highlight(param, lexer, formatter)


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
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\\C-Space": menu-complete')
    readline.parse_and_bind('"\\C-a": beginning-of-line')
    readline.parse_and_bind('"\\C-b": backward-char')
    readline.parse_and_bind('"\\C-e": end-of-line')
    readline.parse_and_bind('"\\C-f": forward-char')
    readline.parse_and_bind('"\\C-h": backward-delete-char')
    readline.parse_and_bind('"\\C-i": complete')
    readline.parse_and_bind('"\\C-j": accept-line')
    readline.parse_and_bind('"\\C-k": "kill-whole-line"')
    readline.parse_and_bind('"\\C-l": clear-screen')
    readline.parse_and_bind('"\\C-m": accept-line')
    if rlcompleter is not None:
        readline.set_completer(rlcompleter.Completer)


def write_history(history_path=None):
    if readline is None:
        return
    if history_path is None:
        history_path = Path("~/.python_history").expanduser()
    readline.write_history_file(history_path)
    logging.info("Written history to %s" % history_path)


def _pythonrc_enable_history():
    """Register readline's history functions with atexit.
    """
    history_path = Path("~/.python_history").expanduser()
    atexit.register(write_history, history_path)
    if not history_path.exists():
        try:
            history_path.touch()
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


def get_height():
    return shutil.get_terminal_size()


def get_width():
    return shutil.get_terminal_size()[1]


def excepthook(exctype, value, traceback):
    """Prints exceptions to sys.stderr and colorizes them.

    Notes
    -----
    traceback.format_exception() isn't used because it's
    inconsistent with the built-in formatter
    """
    old_stderr = sys.stderr
    sys.stderr = StringIO()

    our_hook = cgitb.Hook(format="text", **kwargs)

    try:
        our_hook(exctype, value, traceback)
        stderror = sys.stderr.getvalue()
        ret = pyg_highlight(stderror)
    except UnicodeError:
        old_stderr.write(ret)
    finally:
        sys.stderr = old_stderr


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


def pprinthook(value=None):
    """Pretty print an object to sys.stdout."""
    if value is None:
        return
    help_types = get_help_types()
    if not isinstance(value, help_types):
        return pphighlight(value, width=get_width() or 80)

    # reprstr = format_callable(value)
    reprstr = repr(value)
    sys.stdout.write(reprstr)
    if getattr(value, "__doc__", None):
        sys.stdout.write("\n" + str(pydoc.getdoc(value)) + "\n")


def get_help_types():
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


def source(obj):
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
        sys.stderr.write(
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


if __name__ == "__main__":
    sys.ps1 = "\001\033[0;32m\002>>> \001\033[1;37m\002"
    sys.ps2 = "\001\033[1;31m\002... \001\033[1;37m\002"

    if jedi is not None:
        jedi.settings.auto_import_modules = ['readline', 'pygments', 'pydoc', 'ast']
    # Run installation functions and don't taint the global namespace
    history_path = Path("~/.python_history").expanduser()
    atexit.register(write_history, history_path)
    try:
        # sys.excepthook = excepthook
        if readline is not None:
            _pythonrc_enable_readline()
        _pythonrc_enable_history()
        # sys.displayhook = pprinthook
    except Exception as e:
        print(e)
