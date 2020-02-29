#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up pdb with readline, history management, and fault handling.

Make `pp` use IPython's pretty printer, instead of the standard `pprint` module.

Assumes that the user has IPython, prompt_toolkit, jedi and pygments installed.
prompt_toolkit, jedi and pygments are all dependencies of IPython, so a simple
``pip install -e .`` in the root of this repository can handle this.

In addition, readline is assumed to be present on the system. On systems that don't have readline installed by default, ``pyreadline`` can work as a drop-in replacement.
"""
import atexit
from bdb import BdbQuit, Breakpoint
import cmd
import cgitb
from contextlib import suppress
import faulthandler
import gc
import inspect
import keyword
from logging import getLogger, StreamHandler, BufferingFormatter, Filter
import os
from pathlib import Path
import readline
import pdb
import pydoc
import runpy
import sys
import time
import trace
import tracemalloc
import traceback

from jedi.api import replstartup
from IPython.core.getipython import get_ipython
from IPython.terminal.prompts import Prompts
from prompt_toolkit.completion.fuzzy_completer import FuzzyWordCompleter
from prompt_toolkit.shortcuts import print_formatted_text as print

import pygments
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.token import Token


if sys.version_info < (3, 7):
    from default_profile import ModuleNotFoundError

print(f".pdbrc.py started {time.ctime()}")

# GLOBALS:
log_format = (
    "[ %(name)s : %(relativeCreated)d :] %(levelname)s : %(module)s : --- %(message)s "
)
start = time.time()

logger = getLogger(name=__name__)
handler = StreamHandler()
formatter = BufferingFormatter(linefmt=log_format)
handler.setFormatter(formatter)
logger.addFilter(Filter())
logger.addHandler(handler)
logger.setLevel(30)

debugger_completer = FuzzyWordCompleter(words=keyword.kwlist).get_completions
shell = get_ipython()

cgitb.enable(format="text")
faulthandler.enable()
tracemalloc.start()

# History: Set up separately


def save_history(hist_path=None):
    if not hasattr(locals, "readline"):
        return
    if not hasattr(readline, "append_history_file"):
        print("ERR: no append_history_file method in readline")
        return
    if not hist_path:
        hist_path = Path("~/.pdb_history.py").resolve()
        if not hist_path.exists():
            logger.warning("Creating PDB history file at ~/.pdb_history.")
            hist_path.touch()
        hist_path = hist_path.__fspath__()


try:
    from default_profile.startup import readline_mod
except (ImportError, ModuleNotFoundError):  # noqa
    pass
else:
    readline.parse_and_bind("Tab:menu-complete")


# Customized prompt

class DebuggerPrompt(Prompts):

    def __init__(self):
        self.shell = get_ipython()
        super().__init__(self.shell)

    def python_location(self):
        env = os.environ.get('CONDA_DEFAULT_ENV')
        if env is None:
            return Path(sys.prefix)
        return Path(env)

    def in_prompt_tokens(self):
        return [(Token.Comment, self.python_location()), (Token.Keyword, '<YourPDB> @'), (Token.Keyword, self.shell.execution_count)]

    def __call__(self):
        return self.in_prompt_tokens()

    def __repr__(self):
        return self.in_prompt_tokens()

# Customized Pdb


class MyPdb(pdb.Pdb, cmd.Cmd):

    """Subclass Pdb. Currently defined as a callable.

    Would it prove useful to add dunders for a context manager?

    Notes
    -----

    Here's a comment I found in `bdb.Bdb`.:

        Derived classes and clients can call the following methods
        to manipulate breakpoints.  These methods return an
        error message if something went wrong, None if all is well.
        Set_break prints out the breakpoint line and file:lineno.
        Call self.get_*break*() to see the breakpoints or better
        for bp in Breakpoint.bpbynumber: if bp: bp.bpprint().

    """

    doc_header = ""
    lexer = PythonLexer()
    formatter = TerminalTrueColorFormatter()

    def __init__(
        self, completekey="tab", skip="traitlets", shell=None, *args, **kwargs,
    ):
        """
        To explain all the keyword arguments, pdb inherits from both
        :class:`bdb.Bdb` and :class:`cmd.Cmd`. So pydoc lists a lot
        of attributes on `Pdb` that don't exist on `Bdb`.

        .. todo:: I keep getting errors about self.botframe not being defined?
        """
        self.skip = skip
        self.completekey = completekey
        self.allow_kbdint = True
        self.lineno = None
        super().__init__(completekey=self.completekey, skip=self.skip, *args, **kwargs)
        self.shell = get_ipython() if shell is None else shell
        if self.shell is not None:
            self.prompt = DebuggerPrompt()
        self.bp = Breakpoint

    def __repr__(self):
        """Better repr with :meth:`bdb.Bdb.get_all_breaks` thrown in."""
        return f"<{self.__class__.__name__}:> {self.get_all_breaks()}"

    def run(self, statement, *args, **kwargs):
        """Garbage collect after running because asyncio."""
        try:
            super().run(statement=statement, *args, **kwargs)
        except BdbQuit:
            gc.collect()
            return

    def __call__(self, statement, *args, **kwargs):
        return self.run(statement)

    def colorizer(self, code):
        """color from pygments."""
        if code is not None:
            return pygments.highlight(code, self.lexer, self.formatter)

    def displayhook(self, code):
        """Override the superclasses implementation and use pygments."""
        return self.colorizer(code)

    def completedefault(self):
        """The superclass has this return nothing. Lets have this complete `locals.keys()`"""
        self.complete(sorted(locals().keys()))

    # FUCK. pdb assigns to this too?
    # @property
    # def curframe(self):
    #     """Gettin errors because pdb's preloop needs curframe. Has to be a property because we use the attributes on the frame"""
    #     return inspect.currentframe()

    def do_raise(self, exception):
        # Seriously why the fuck wouldn't this stop popping up
        if isinstance(exception, Exception):
            raise exception
        else:
            return

    def curframe_locals(self):
        return self.curframe.f_locals()

    def message(self, msg):
        return self.colorizer(super().message(msg))

    @staticmethod
    def help():
        # Ill concede this has nothing to do with anything but I find it helpful
        pydoc.pipepager(inspect.getsource(pdb.Pdb), os.environ.get("PAGER"))


debugger = MyPdb(shell=get_ipython())


def exception_hook(type=None, value=None, tb=None):
    """Return to debugger after fatal exception (Python cookbook 14.5)."""
    if type or value or tb is None:
        type, value, tb = sys.exc_info()
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    traceback.print_exception(type, value, tb)
    pdb.pm()


# sys.excepthook = exception_hook

end = time.time()
duration = end - start
print(f".pdbrc.py finished.{time.ctime()}" + "\n" + f"duration was: {duration}.")

malloced = tracemalloc.take_snapshot()
