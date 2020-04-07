#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up pdb with readline, history management, and fault handling.

Make `pp` use IPython's pretty printer, instead of the standard `pprint` module.

Assumes that the user has IPython, prompt_toolkit, jedi and pygments installed.
prompt_toolkit, jedi and pygments are all dependencies of IPython, so a simple
``pip install -e .`` in the root of this repository can handle this.

In addition, readline is assumed to be present on the system. On systems that don't have readline installed by default, ``pyreadline`` can work as a drop-in replacement.
"""
# {{{
import __main__
import argparse
import builtins
import cgitb
import faulthandler
import gc
import io
import importlib
import inspect
import keyword
import os
import pdb
import platform
import pydoc
import runpy
import sys
import time
import traceback
from bdb import BdbQuit, Breakpoint
from contextlib import contextmanager
from logging import BufferingFormatter, Filter, StreamHandler, getLogger
from pathlib import Path
from pdb import Pdb, Restart
from textwrap import dedent
from typing import Any, AnyStr, Union, TYPE_CHECKING

import ipdb
import pygments
from IPython.core.getipython import get_ipython
from IPython.core.magics.namespace import NamespaceMagics
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.prompts import Prompts

from prompt_toolkit.completion.fuzzy_completer import FuzzyWordCompleter
from prompt_toolkit.shortcuts import (
    print_formatted_text,
)  # don't replace this with print

# It just errored on Win32 because the output didn't get initialized correctly
if platform.platform().startswith("Win32"):
    from prompt_toolkit.output.windows10 import Windows10_Output
else:
    Windows10_Output = None

    from ipykernel.zmqshell import ZMQInteractiveShell
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.python import PythonLexer
from pygments.token import Token

try:
    import readline
except ImportError:
    readline = None

try:
    from gruvbox.gruvbox import GruvboxStyle
except ImportError:
    from pygments.styles.inkpot import InkPotStyle

    pdb_style = InkPotStyle()
else:
    pdb_style = GruvboxStyle()

if sys.version_info < (3, 7):
    from default_profile import ModuleNotFoundError

try:
    from default_profile.startup import readline_mod
except (ImportError, ModuleNotFoundError):  # noqa
    pass
else:
    readline.parse_and_bind("Tab:menu-complete")
# }}}

print(f".pdbrc.py started {time.ctime()}")

# GLOBALS: {{{
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

if Windows10_Output is not None:
    output = Windows10_Output(io.StringIO())

nsmagics = NamespaceMagics()
pinfo = nsmagics.pinfo
pinfo2 = nsmagics.pinfo2
pdef = nsmagics.pdef
psource = nsmagics.psource

# }}}

# History: Set up separately {{{


def save_history(hist_path=None):
    if not hasattr(locals, "readline"):
        return
    if not hasattr(readline, "append_history_file"):
        print("ERR: no append_history_file method in readline")
        return
    if not hist_path:
        hist_path: Union[Path, str, Any] = Path("~/.pdb_history.py").resolve()
        if not hist_path.exists():
            logger.warning("Creating PDB history file at ~/.pdb_history.")
            hist_path.touch()
        return str(hist_path)  # }}}


def get_parser():  # {{{
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
        type=argparse.FileType("r"),
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
        default=False,
        action='store_true',
    )

    parser.add_argument("-v", "--version", action="version")

    return parser  # }}}


# Customized Prompt: {{{


class DebuggerPrompt(Prompts):
    """Create a customized prompt for the debugger."""

    shell = get_ipython()

    def __init__(self, shell=None, **kwargs):
        self.shell = shell or get_ipython()
        if self.shell is not None:
            if not isinstance(self.shell, ZMQInteractiveShell):
                self.old_prompt = self.shell.prompts
                super().__init__(self.shell, **kwargs)

    def _is_vi_mode(self):
        """We don't have to make this but my god look at the original implementation."""
        return getattr(self.shell.pt_app, "editing_mode", None)

    def vi_mode(self):
        if self._is_vi_mode():
            return self.shell.pt_app.app.vi_state.input_mode

    @staticmethod
    def python_location():
        """The location of the python executable.

        :return:
        :rtype: Path
        """
        env = os.environ.get("CONDA_DEFAULT_ENV")
        if env is None:
            return Path(sys.prefix)
        return Path(env)

    def in_prompt_tokens(self):
        prompt = [
            (Token.Comment, self.python_location()),
            (Token.Keyword, "<YourPDB> @"),
            (Token.Keyword, self.shell.execution_count),
        ]

        if self.shell.prompt_includes_vi_mode:
            prompt.insert(0, (Token.Literal.String, self.vi_mode()))
        return prompt

    def __call__(self):
        return self.in_prompt_tokens()

    def __repr__(self):
        return self.in_prompt_tokens()

    def __len__(self):
        """Define length of the instance by the superclasses `_width`."""
        return self._width()  # }}}


def _init_pdb(context=3, commands=None, debugger_kls=None):  # {{{
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

    doc_header = "Whew!"

    lexer = PythonLexer()
    # why the fuck is this erroring
    # formatter = TerminalTrueColorFormatter(style=pdb_style.styles.items())
    formatter = TerminalTrueColorFormatter()

    def __init__(
        self, completekey="tab", skip="traitlets", _shell=None, *args, **kwargs,
    ):
        """
        To explain all the keyword arguments, pdb inherits from both
        :class:`bdb.Bdb` and :class:`cmd.Cmd`. So pydoc lists a lot
        of attributes on `Pdb` that don't exist on `Bdb`.

        .. todo:: I keep getting errors about self.botframe not being defined?
        """
        self.skip = skip
        self.completekey = completekey
        self.allow_kbdint = False
        self.lineno = None

        self.stack = []
        self.curindex = 0
        self.curframe = inspect.currentframe()
        # keep this above super because cmd uses prompt. and shell above prompt
        self.shell = get_ipython() if _shell is None else _shell
        self.prompt = (
            DebuggerPrompt(self.shell) if self.shell is not None else "YourPdb: "
        )
        super().__init__(completekey=self.completekey, skip=self.skip, *args, **kwargs)

        self._wait_for_mainpyfile = False
        self._user_requested_quit = True
        self.forget()
        self.execRcLines()

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

    def colorizer(self, code: AnyStr) -> Any:
        """color from pygments."""
        if code is not None:
            return pygments.highlight(
                code, self.lexer, self.formatter, outfile=sys.stdout
            )

    def displayhook(self, code):
        """Override the superclasses implementation and use pygments."""
        return self.colorizer(code)

    def completedefault(self):
        """The superclass has this return nothing. Lets have this complete `locals.keys()`"""
        self.complete(sorted(locals().keys()))

    def _runmodule(self, module_name):
        self._wait_for_mainpyfile = True
        self._user_requested_quit = False
        # noinspection PyProtectedMember
        mod_name, mod_spec, code = runpy._get_module_details(module_name)
        self.mainpyfile = self.canonic(code.co_filename)

        __main__.__dict__.clear()
        __main__.__dict__.update(
            {
                "__name__": "__main__",
                "__file__": self.mainpyfile,
                "__package__": mod_spec.parent,
                "__loader__": mod_spec.loader,
                "__spec__": mod_spec,
                "__builtins__": builtins,
            },
        )
        self.run(code)

    def _debug_post_mortem(self):
        self.shell.debugger(force=True)

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

    # TODO:
    # def default(self):
    #     return

    def do_import(self, mod):
        return importlib.import_module(mod)


debugger = MyPdb(_shell=get_ipython())  # }}}


def wrap_sys_excepthook():
    """Make sure we wrap it only once or we would end up with a cycle.

    As it's written don't we lose the old sys excepthook as soon as we leave
    this functions ns though?

    Also how do you compare Exceptions and whatever excepthook is?
    """
    if sys.excepthook != BdbQuit:
        original_excepthook = sys.excepthook
        sys.excepthook = BdbQuit


def set_trace(frame=None, context=3):
    # wrap_sys_excepthook()
    if frame is None:
        # noinspection PyProtectedMember
        frame = sys._getframe().f_back
    p = _init_pdb(context).set_trace(frame)
    if p and hasattr(p, "shell"):
        p.shell.restore_sys_module_state()


def post_mortem(tb: traceback = None) -> None:
    """Wrap `sys_excepthook`.

    .. todo::
        Are there situations where sys.exc_info[2] returns None but sys.last_traceback
        doesn't?

    """
    p = _init_pdb()
    p.reset()
    if tb is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        tb = sys.exc_info()[2]
    if tb:
        p.interaction(None, tb)


def pm():
    post_mortem(sys.last_traceback)


def _run(statement, global_dict=None, local_dict=None):
    """Sorry but run overlaps with the magic `%run`!"""
    _init_pdb().run(statement, global_dict, local_dict)


def runcall(*args, **kwargs):
    return _init_pdb().runcall(*args, **kwargs)


def runeval(expression, global_dict=None, local_dict=None):
    return _init_pdb().runeval(expression, global_dict, local_dict)


@contextmanager
def launch_ipdb_on_exception(*args, **kwargs):
    """Context manager for running code with a debugger fallback.

    Accepts any args and returns them as is to ensure that code can be left in place.
    """
    try:
        yield
    except Exception:  # noqa
        if hasattr(sys, "exc_info"):
            print(sys.exc_info()[2])
        post_mortem(sys.last_traceback)
    finally:
        return args, kwargs


def exception_hook(etype=None, value=None, tb=None):
    """Return to debugger after fatal exception (Python cookbook 14.5)."""
    if etype or value or tb is None:
        etype, value, tb = sys.exc_info()
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(etype, value, tb)
    traceback.print_exception(etype, value, tb)
    pdb.pm()


# sys.excepthook = exception_hook

end = time.time()
duration = end - start
print(f".pdbrc.py finished.{time.ctime()}" + "\n" + f"duration was: {duration}.")


def debug_script(namespace, script=None):
    if script is None:
        return
    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = _init_pdb(commands=namespace.commands)

    try:
        # noinspection PyProtectedMember
        pdb._runscript(script)
        # noinspection PyProtectedMember
        if pdb._user_requested_quit:
            return
        logger.warning("The program finished and will be restarted")
    except Restart:
        logger.info(f"Restarting {script} with arguments:\t{str(sys.argv[1:])}")
    except BdbQuit:
        logger.critical("Quit signal received.  Goodbye!")
    except EOFError:
        sys.exit("EOF caught. Goodbye!")
    except KeyboardInterrupt:
        sys.exit("KeyboardInterrupt caught. Goodbye!")
    except SystemExit:
        # In most cases SystemExit does not warrant a post-mortem session.
        print("The program exited via sys.exit(). Exit status: ", end="")
        print(sys.exc_info()[1])
    except Exception:
        traceback.print_exc()
        print("Uncaught exception. Entering post mortem debugging")
        print("Running 'cont' or 'step' will restart the program")
        t = sys.exc_info()[2]
        pdb.interaction(None, t)
        print("Post mortem debugger finished. The " + script + " will be restarted")


def get_or_start_ipython():
    """Returns the global IPython instance.

    Summary
    -------

    Extended Summary
    ----------------
    In contrast to `IPython.core.getipython.get_ipython`, this will start
    IPython if `get_ipython` returns None.

    Builds a terminal app in order to force IPython to load the
    user's configuration.
    `IPython.terminal.TerminalIPythonApp.interact` is set to False to
    avoid output (banner, prints) and then the TerminalIPythonApp is
    initialized with '--no-term-title'.
    """
    shell = get_ipython()
    if shell is None:
        ipapp = TerminalIPythonApp()
        ipapp.interact = False
        ipapp.initialize(["--no-term-title"])
        shell = ipapp.shell
    else:
        # Detect if embed shell or not and display a message
        if isinstance(shell, InteractiveShellEmbed):
            sys.stderr.write(
                "\nYou are currently into an embedded ipython shell,\n"
                "the configuration will not be loaded.\n\n"
            )
    shell.interact()


def main():
    """Parses users argument and dispatches based on responses."""
    program_name, *args = sys.argv
    parser = get_parser()
    if len(args) == 1:
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
    else:
        if hasattr(namespace, "interactive"):
            if namespace.interactive:
                get_or_start_ipython()

    mainpyfile = namespace.mainpyfile
    # Replace pdb's dir with script's dir in front of module search path.
    if mainpyfile is not None:
        sys.path.insert(0, os.path.dirname(mainpyfile))
        debug_script(namespace, mainpyfile)


main()
