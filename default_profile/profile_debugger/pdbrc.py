#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up pdb with readline, history management, and fault handling.

Make `pp` use IPython's pretty printer, instead of the standard `pprint` module.

Assumes that the user has IPython, prompt_toolkit, jedi and pygments installed.
prompt_toolkit, jedi and pygments are all dependencies of IPython, so a simple
``pip install -e .`` in the root of this repository can handle this.

In addition, readline is assumed to be present on the system. On systems that don't have readline installed by default, ``pyreadline`` can work as a drop-in replacement.
"""
import argparse
import atexit
from bdb import BdbQuit, Breakpoint
import cmd
import cgitb
from contextlib import suppress, contextmanager
import faulthandler
import gc
import inspect
import keyword
from logging import getLogger, StreamHandler, BufferingFormatter, Filter
import os
from pathlib import Path
import readline
import pdb
from pdb import Restart, Pdb
import pydoc
import runpy
import sys
from textwrap import dedent
import time
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


def get_parser():
    """Factored out of main. Well sweet this now rasies an error."""
    parser = argparse.ArgumentParser(
        prog="ipdb+",
        description=(
            "\nAn IPython flavored version of pdb with even more useful features."
            "\nWhy?\nYou're debugging code you don't want to figure out if you"
            " imported something or not.\n\n"
        ),
    )

    parser.add_argument(
        "-f",
        "--file",
        action="store",
        dest="mainpyfile",
        help="File to run under the debugger.",
    )

    parser.add_argument(
        "-c",
        "--commands",
        nargs="*",
        type=list,
        help="List of commands to run before starting.",
        default=[],
        action="append",
    )

    parser.add_argument(
        "-m",
        "--module",
        nargs="+",
        help=dedent(
            "Module to debug. Note that the provided module will be subject"
            " to all the standard rules that any imported module would be"
            " as per the import rules specified in the language/library"
            " references."
        ),
        dest="mod",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        help="Force interactivity if pdb would otherwise exit.",
        const=True,
        nargs="?",
        default=False,
    )

    parser.add_argument("-v", "--version", action="version")

    return parser


# Customized prompt


class DebuggerPrompt(Prompts):
    def python_location(self):
        env = os.environ.get("CONDA_DEFAULT_ENV")
        if env is None:
            return Path(sys.prefix)
        return Path(env)

    def in_prompt_tokens(self):
        return [
            (Token.Comment, self.python_location()),
            (Token.Keyword, "<YourPDB> @"),
            (Token.Keyword, self.shell.execution_count),
        ]

    def __call__(self):
        return self.in_prompt_tokens()

    def __repr__(self):
        return self.in_prompt_tokens()

    def __len__(self):
        """Define length of the instance by the superclasses `_width`."""
        return self._width()


# Customized Pdb


def _init_pdb(context=3, commands=None, debugger_kls=None):
    """Needed to add a debugger_cls param to this."""
    if debugger_kls is None:
        if MyPdb is not None:
            debugger_kls = MyPdb
        elif ipdb is not None:
            debugger_kls = ipdb
        else:
            debugger_kls = Pdb
    if commands is None:
        commands = []
    try:
        p = debugger_kls(context=context)
    except TypeError:
        p = debugger_kls()
    p.rcLines.extend(commands)
    return p


class MyPdb(pdb.Pdb):

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
        self.prompt = (
            DebuggerPrompt(self.shell) if self.shell is not None else "YourPdb: "
        )
        self.curframe = inspect.currentframe()
        self._wait_for_mainpyfile = False
        self._user_requested_quit = True

    def __repr__(self):
        """Better repr with :meth:`bdb.Bdb.get_all_breaks` thrown in."""
        return f"<{self.__class__.__name__}:> {self.get_all_breaks()}"

    def run(self, statement, *args, **kwargs):
        """Garbage collect after running because asyncio."""
        try:
            super().run(statement, *args, **kwargs)
        except BdbQuit:
            gc.collect()
            return

    # def __call__(self, statement, *args, **kwargs):
    #     return self.run(statement)

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

    def _runmodule(self, module_name):
        self._wait_for_mainpyfile = True
        self._user_requested_quit = False
        import runpy

        mod_name, mod_spec, code = runpy._get_module_details(module_name)
        self.mainpyfile = self.canonic(code.co_filename)
        import __main__

        __main__.__dict__.clear()
        __main__.__dict__.update(
            {
                "__name__": "__main__",
                "__file__": self.mainpyfile,
                "__package__": mod_spec.parent,
                "__loader__": mod_spec.loader,
                "__spec__": mod_spec,
                "__builtins__": __builtins__,
            }
        )
        self.run(code)

    def curframe_locals(self):
        return self.curframe.f_locals()

    def message(self, msg):
        return self.colorizer(super().message(msg))

    def do_helper(self):
        # Ill concede this has nothing to do with anything but I find it helpful
        # we should bind an instance of pydoc.Helper to this class those suckers are useful.
        pydoc.pipepager(inspect.getsource(pdb.Pdb), os.environ.get("PAGER"))

    @property
    def bp(self, *args, **kwargs):
        return Breakpoint(*args, **kwargs)


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


def debug_script(script=None):
    if script is None:
        return
    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = _init_pdb(commands=namespace.commands)

    try:
        pdb._runscript(script)
        if pdb._user_requested_quit:
            return
        logger.warning("The program finished and will be restarted")
    except Restart:
        logger.info(f"Restarting {script} with arguments:\t{str(sys.argv[1:])}")
    except BdbQuit:
        logger.critical("Quit signal received.  Goodbye!")

    except SystemExit:
        # In most cases SystemExit does not warrant a post-mortem session.
        print("The program exited via sys.exit(). Exit status: ", end="")
        print(sys.exc_info()[1])
    except:
        traceback.print_exc()
        print("Uncaught exception. Entering post mortem debugging")
        print("Running 'cont' or 'step' will restart the program")
        t = sys.exc_info()[2]
        pdb.interaction(None, t)
        print("Post mortem debugger finished. The " + script + " will be restarted")


def main():
    """Parses users argument and dispatches based on responses."""
    program_name, *args = sys.argv
    parser = get_parser()
    if not args:
        # Print some help, then don't do the other junk here
        parser.print_help()
        return

    try:
        namespace = parser.parse_args(args)
    except SystemExit:
        # can't believe i'm catching sysexit but fuck you argparse
        namespace = None

    if hasattr(namespace, "mainpyfile"):
        if namespace.mainpyfile is not None:
            if not Path(namespace.mainpyfile).exists():
                raise FileNotFoundError
            # else: dedent 2 tabs if uncommenting
            #     _init_pdb().set_trace()

            # Replace pdb's dir with script's dir in front of module search path.
            sys.path.insert(0, os.path.dirname(namespace.mainpyfile))
            debug_script(namespace.mainpyfile)
    elif hasattr(namespace, "mod"):
        _init_pdb()._runmodule(mod)


if __name__ == "__main__":
    main()
