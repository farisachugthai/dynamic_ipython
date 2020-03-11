# -*- coding: utf-8 -*-
"""Startup script that adds niceties to the interactive interpreter.

This script adds the following things:

- Readline bindings, tab completion, and history (in ~/.history/python,
  which can be disabled by setting NOHIST in the environment)

- Pretty printing of expression output (with Pygments highlighting)

- Pygments highlighting of tracebacks

- Function arguments in repr() for callables

- A source() function that displays the source of an arbitrary object
  (in a pager, with Pygments highlighting)

Python 2.3 and newer are supported, including Python 3.x.

Note: The default versions of Python that ship with Mac OS X don't
come with readline. To get readline support, you can try a stand-alone
readline library[1], or you can use a different Python distribution
(like the one from MacPorts).

[1]: http://pypi.python.org/pypi/readline
"""
import atexit
import builtins
import cgitb
import functools
import inspect
from inspect import findsource, getmodule, getsource, getsourcefile
from io import StringIO
import linecache
from linecache import cache
import logging
import os
from pathlib import Path
import types
import pydoc
from pydoc import pager
import pprint
import re
import shutil
import sys

logging.basicConfig(level=logging.WARNING)
cgitb.enable(format="text")

try:
    import readline
except ImportError:
    logging.error("readline unavailable - tab completion disabled.\n")
    readline = None

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer, PythonTracebackLexer
    from pygments.formatters import TerminalFormatter
except ImportError:
    pass

try:
    import jedi
except:
    jedi = None
else:
    from jedi.api import replstartup


def pyg_highlight(param):
    """Run a string through the pygments highlighter."""
    return highlight(param, PythonLexer(), TerminalFormatter())


def complete(text, state):
    old_complete = readline.get_completer()
    if not text:
        # Insert four spaces for indentation
        return ("    ", None)[state]
    else:
        return old_complete(text, state)


def _pythonrc_enable_readline():
    """Enable readline, tab completion, and history"""
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)


has_written = False


def write_history(history_path):
    if readline is None:
        return
    readline.write_history_file(history_path)
    logging.info("Written history to %s" % history_path)
    has_written = True


def _pythonrc_enable_history():
    """Register readline's history functions with atexit.

    "NOHIST= python" will disable history.
    """
    if os.environ.get("NOHIST"):
        return
    if readline is None:
        return
    history_path = Path("~/.python_history").expanduser()
    if not history_path.exists():
        history_path.touch()
    if os.path.isfile(history_path):
        try:
            readline.read_history_file(history_path)
        except OSError:
            pass

    if not has_written:
        write_history(history_path)
    atexit.register(write_history, history_path)
    readline.set_history_length(-1)


def pphighlight(o, *a, **kw):
    """Lex a `pprint.pformat`ted string, pass it through `pyg_highlight` then rerun it through pygments.highlight."""
    s = pprint.pformat(o, *a, **kw)
    try:
        sys.stdout.write(highlight(s, PythonLexer(), TerminalFormatter()))
    except UnicodeError:
        sys.stdout.write(s)
        sys.stdout.write("\n")


def highlighter(func, *args, **kwargs):
    """Decorator to run a function through `pphighlight`."""

    @functools.wraps
    def _():
        return pphighlight(func, *args, **kwargs)


def get_width():
    return shutil.get_terminal_size()[1]


def _pythonrc_enable_pprint():
    """Enable pretty printing of evaluated expressions"""

    _old_excepthook = sys.excepthook

    def excepthook(exctype, value, traceback):
        """Prints exceptions to sys.stderr and colorizes them"""
        # traceback.format_exception() isn't used because it's
        # inconsistent with the built-in formatter
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            _old_excepthook(exctype, value, traceback)
            stderror = sys.stderr.getvalue()
            try:
                ret = pyg_highlight(
                    stderror
                )
            except UnicodeError:
                pass
                old_stderr.write(ret)
            finally:
                sys.stderr = old_stderr

            sys.excepthook = excepthook
        except ImportError:
            pphighlight = pprint.pprint

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

    if hasattr(inspect, "getfullargspec"):
        getargspec = inspect.getfullargspec
    else:
        getargspec = inspect.getargspec

    def pprinthook(value):
        """Pretty print an object to sys.stdout and also save it in the sys.displayhook.
        """

        if value is None:
            return
        builtins._ = value

        if isinstance(value, help_types):
            reprstr = repr(value)
            try:
                if inspect.isfunction(value):
                    parts = reprstr.split(" ")
                    parts[1] += inspect.formatargspec(*getargspec(value))
                    reprstr = " ".join(parts)
                elif inspect.ismethod(value):
                    parts = reprstr[:-1].split(" ")
                    parts[2] += inspect.formatargspec(*getargspec(value))
                    reprstr = " ".join(parts) + ">"
            except TypeError:
                pass
            sys.stdout.write(reprstr)
            sys.stdout.write("\n")
            if getattr(value, "__doc__", None):
                sys.stdout.write("\n")
                sys.stdout.write(pydoc.getdoc(value))
                sys.stdout.write("\n")
        else:
            pphighlight(value, width=get_width() or 80)

    sys.displayhook = pprinthook


def _pythonrc_fix_linecache():
    """Add source(obj) that shows the source code for a given object.

    linecache.updatecache() replacement that actually works with zips.
    See http://bugs.python.org/issue4223 for more information.
    """

    def updatecache(filename, module_globals=None):
        """Update a cache entry and return its list of lines.

        If something's wrong, print a message, discard the cache entry,
        and return an empty list.
        """

        if filename in cache:
            del cache[filename]
        if not filename or filename[0] + filename[-1] == "<>":
            return []

        fullname = filename
        try:
            stat = os.stat(fullname)
        except os.error:
            basename = os.path.split(filename)[1]

            if module_globals and "__loader__" in module_globals:
                name = module_globals.get("__name__")
                loader = module_globals["__loader__"]
                get_source = getattr(loader, "get_source", None)

                if name and get_source:
                    try:
                        data = get_source(name)
                    except (ImportError, IOError):
                        pass
                    else:
                        if data is None:
                            return []
                        cache[filename] = (
                            len(data),
                            None,
                            [line + "\n" for line in data.splitlines()],
                            fullname,
                        )
                        return cache[filename][2]

            for dirname in sys.path:
                try:
                    fullname = os.path.join(dirname, basename)
                except (TypeError, AttributeError):
                    pass
                else:
                    try:
                        stat = os.stat(fullname)
                        break
                    except os.error:
                        pass
            else:
                return []
        try:
            with open(fullname, "rt+") as f:
                lines = f.readlines()
        except OSError:
            return []
        size, mtime = stat.st_size, stat.st_mtime
        cache[filename] = size, mtime, lines, fullname
        return lines

    linecache.updatecache = updatecache


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

    # Run installation functions and don't taint the global namespace
    try:
        _pythonrc_enable_readline()
        _pythonrc_enable_history()
        _pythonrc_enable_pprint()
        _pythonrc_fix_linecache()
    finally:
        if os.path.curdir is not None:
            sys.path.insert(0, os.path.curdir)
