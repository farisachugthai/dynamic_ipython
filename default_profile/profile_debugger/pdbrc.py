#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up pdb with readline, history management, and fault handling.

Make `pp` use IPython's pretty printer, instead of the standard `pprint` module.

:URL: https://nedbatchelder.com/blog/200704/my_pdbrc.html

Jesus Christ this got out of control.

"""
import atexit
from bdb import BdbQuit, Breakpoint
import cgitb
from contextlib import suppress
import faulthandler
import gc
import inspect
import keyword
from logging import getLogger, StreamHandler, BufferingFormatter, Filter
from pathlib import Path
import pdb
import pydoc
import rlcompleter
import runpy
import sys
import time
import trace
import traceback

# Run all this before any non-std lib imports. They should get profiled too
print(f".pdbrc.py started {time.ctime()}")

log_format = (
    "[ %(name)s : %(relativeCreated)d :] %(levelname)s : %(module)s : --- %(message)s "
)
start = time.time()

logger = getLogger(name=__name__)
handler = StreamHandler()
formatter = BufferingFormatter(linefmt=log_format)
handler.setFormatter(formatter)
logger.addFilter(logging.Filter())
logger.addHandler(handler)
logger.setLevel(30)

faulthandler.enable()
cgitb.enable(format="text")

try:
    from prompt_toolkit.shortcuts import print_formatted_text as print
except:  # noqa
    from pprint import pprint as print
    debugger_completer = rlcompleter.Completer.complete
else:
    from prompt_toolkit.completion.fuzzy_completer import FuzzyWordCompleter
    debugger_completer = FuzzyWordCompleter(words=keyword.kwlist).get_completions


try:
    from IPython.core.getipython import get_ipython
except:  # noqa
    shell = None
else:
    shell = get_ipython()


# Use IPython's pretty printing within PDB
with suppress(ImportError):
    from IPython.lib.pretty import pprint


with suppress(ImportError):
    from jedi.api import replstartup

try:
    import readline
except:
    pass
else:# this makes completions look classic IPython style
    readline.parse_and_bind("Tab:menu-complete")

# I have a really useful module for importing readline on windows, linux,
# WSL, and anything else you can imagine. let's use it.
try:
    from default_profile.startup import __main__
except:  # noqa
    pass
else:

    readline_mod = runpy.run_path(
        Path("../startup/30_readline.py").__fspath__(), init_globals=globals()
    )
    # runpy.run_path returns a dict with the modules namespace so let's get
    # the keys and check if we imported readline
    if "readline" in readline_mod.keys():
        readline = readline_mod["readline"]
    if "setup_readline" in readline_mod.keys():
        setup_readline = readline_mod["setup_readline"]
        setup_readline()


def save_history(hist_path=None):
    if not hasattr(locals, 'readline'):
        return
    if not hasattr(readline, "append_history_file"):
        print("ERR: no append_history_file method in readline")
        return
    if not hist_path:
        hist_path = Path("~/.pdb_history.py").resolve()
        if not hist_path.exists():
            logging.warning("Creating PDB history file at ~/.pdb_history.")
            hist_path.touch()
        hist_path = hist_path.__fspath__()

    readline.append_history_file(hist_path)


# History: Set up separately
try:
    from default_profile.startup import readline_mod
except:  # noqa
    historyPath = Path.expanduser("~/.pdb_history.py")

    if historyPath.exists():
        readline.read_history_file(historyPath)
        save_history(historyPath)

    atexit.register(save_history, hist_path=historyPath)
else:

    readline_mod.setup_historyfile("~/.pdb_history")

# Yes I'm still importing stuff

try:
    import pygments
except ImportError:
    colorizer = None
else:
    from pygments.lexers.python import PythonLexer
    from pygments.formatters.terminal256 import TerminalTrueColorFormatter

    lexer = PythonLexer()
    formatter = TerminalTrueColorFormatter()


    def colorizer(code):
        return pygments.highlight(code, lexer, formatter)

# Customized Pdb


class MyPdb(pdb.Pdb):
    """Subclass Pdb."""
    prompt = f"<YourPdb> : "
    doc_header = ""

    def __init__(
        self,
        completekey='tab',
        skip="traitlets",
        prompt=None,
        doc_header=None,
        shell=None,
        *args,
        **kwargs,
    ):
        """
        To explain all the keyword arguments, pdb inherits from both
        :class:`bdb.Bdb` and :class:`cmd.Cmd`. So pydoc lists a lot
        of attributes on `Pdb` that don't exist on `Bdb`.

        .. todo:: I keep getting errors about self.botframe not being defined?
        """
        self.skip = skip
        self.prompt = prompt
        self.doc_header = doc_header
        self.shell = shell
        if self.shell is not None:
            self.prompt += " [" + self.shell.execution_count + "]: "
        self.bp = Breakpoint
        self.completekey = completekey

        super().__init__(completekey=self.completekey, skip=self.skip, *args, **kwargs)

    def __repr__(self):
        """Better repr with :meth:`bdb.Bdb.get_all_breaks` thrown in."""
        return f"<{self.__class__.__name__} {self.get_all_breaks()}"

    def run(self, statement, *args, **kwargs):
        """Garbage collect after running because asyncio."""
        try:
            super().run(statement=statement, *args, **kwargs)
        except BdbQuit:
            gc.collect()
            return

    def __call__(self, statement):
        return self.run(statement)

    def completedefault(self):
        """The superclass has this return nothing. Lets have this complete `locals.keys()`"""
        self.complete(sorted(locals().keys()))

    def message(self, msg):
        if colorizer is not None:
            return colorizer(super().message(msg))

    @staticmethod
    def help():
        # Ill concede this has nothing to do with anything but I find it helpful
        pydoc.pipepager(inspect.getsource(pdb.Pdb), os.environ.get('PAGER'))


debugger = MyPdb()
# TODO:
# get_ipython().debugger_cls = MyPdb
# Customize the sys.excepthook


def exception_hook(type=None, value=None, tb=None):
    """Return to debugger after fatal exception (Python cookbook 14.5)."""
    if type or value or tb is None:
        type, value, tb = sys.exc_info()
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    traceback.print_exception(type, value, tb)
    pdb.pm()


sys.excepthook = exception_hook

end = time.time()
duration = end - start
print(f".pdbrc.py finished.{time.ctime()}\nduration was: {duration}.\n")
