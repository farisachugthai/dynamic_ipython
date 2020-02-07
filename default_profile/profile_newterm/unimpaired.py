#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from bdb import BdbQuit
import code
import cgitb
import faulthandler
import functools
import logging
import os
import pathlib
from pathlib import Path
import pdb
from reprlib import Repr
import reprlib

try:
    import readline
except ImportError:
    readline = None

import runpy
import rlcompleter
import sys
import trace
import traceback
from types import SimpleNamespace

from IPython.core.getipython import get_ipython
from IPython.core.profiledir import ProfileDir
from IPython.terminal.interactiveshell import TerminalInteractiveShell

import prompt_toolkit
from prompt_toolkit import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.shortcuts import PromptSession

import traitlets
from traitlets.config.loader import Config
from traitlets.config.application import Application
from traitlets.traitlets import TraitError

from IPython.core.magics.basic import BasicMagics
from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShellABC
from IPython.core.profiledir import ProfileDir, ProfileDirError
from IPython.extensions.storemagic import StoreMagics
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.terminal.prompts import RichPromptDisplayHook

import jedi
from jedi.api import replstartup

import pygments
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

try:
    import trio
except:
    trio = None

logging.basicConfig(level=logging.INFO)


class TerminallyUnimpaired(TerminalInteractiveShell):
    """What do we need to implement?

    Assuming this'll crash then we can notate what was required.

    We crashed on loading magics? Weird.
    Uhh I'm just gonna add a Config to ensure that it's there.

    """

    def init(self):
        self.interactive_console = code.InteractiveConsole()
        self.lexer = pygments.lexers.python.Python3Lexer()
        self.formatter = TerminalTrueColorFormatter()
        self.Path = Path

        # Should make an else. *shrugs*
        self.ipython_dir = os.path.expanduser('~/.ipython')
        self.profile_dir = ProfileDir()
        self._profile_dir = os.path.expanduser('~/.ipython/profile_default')

    def __init__(self, user_module=None, **kwargs):

        # This is where traits with a config_key argument are updated
        # from the values on config.
        self.configurables = [self]

        self.init()

        # These are relatively independent and stateless
        self.init_instance_attrs()
        self.init_environment()

        # Check if we're in a virtualenv, and set up sys.path.
        self.init_virtualenv()

        # Create namespaces (user_ns, user_global_ns, etc.)
        user_ns = locals()
        self.init_create_namespaces(user_module, user_ns)
        # This has to be done after init_create_namespaces because it uses
        # something in self.user_ns, but before init_sys_modules, which
        # is the first thing to modify sys.
        # TODO: When we override sys.stdout and sys.stderr before this class
        # is created, we are saving the overridden ones here. Not sure if this
        # is what we want to do.
        self.save_sys_module_state()
        self.init_sys_modules()

        sys.stdout.reconfigure(line_buffering=True)

        # While we're trying to have each part of the code directly access what
        # it needs without keeping redundant references to objects, we have too
        # much legacy code that expects ip.db to exist.
        # self.db = PickleShareDB(os.path.join(self.profile_dir.location, "db"))
        pdb.set_trace()
        self.history_dir = Path(self.profile_dir.location + 'log')
        self.history = FileHistory(self.history_dir)
        self.init_history()
        self.init_encoding()
        self.init_prefilter()

        self.init_syntax_highlighting()
        self.init_hooks()
        self.init_events()
        self.init_pushd_popd_magic()
        self.init_logger()
        self.init_builtins()

        self.init_prompt_toolkit_cli()

        # The following was in post_config_initialization
        self.init_inspector()
        self.raw_input_original = input
        self.init_completer()
        # TODO: init_io() needs to happen before init_traceback handlers
        # because the traceback handlers hardcode the stdout/stderr streams.
        # This logic in in debugger.Pdb and should eventually be changed.
        self.init_io()
        self.init_prompts()
        self.init_display_formatter()
        self.pdb = True
        self.call_pdb = self.pdb
        self.InteractiveTB = SimpleNameSpace()
        self.init_display_pub()
        self.init_data_pub()
        self.init_displayhook()
        self.init_magics()
        self.init_alias()
        self.init_logstart()
        self.init_extension_manager()
        self.init_payload()
        self.init_deprecation_warnings()
        self.hooks.late_startup_hook()
        self.events.trigger("shell_initialized", self)
        atexit.register(self.atexit_operations)

        # The trio runner is used for running Trio in the foreground thread. It
        # is different from `_trio_runner(async_fn)` in `async_helpers.py`
        # which calls `trio.run()` for every cell. This runner runs all cells
        # inside a single Trio event loop. If used, it is set from
        # `ipykernel.kernelapp`.
        self.trio_runner = None


        # mine
        self.create_completer()
        self.create_kb()
        self.init_profile_dir()
        self.begin()

    def __repr__(self):
        return f"<{self.__class__.__name__}> {reprlib.Repr().repr_dict(self.traits(), level=50)}"

    def showsyntaxerror(self, *args, **kwargs):
        """Override the superclasses so we can ignore IPython's inconsistent way of calling this."""
        return self.interactive_console.showsyntaxerror(*args, **kwargs)

    def showtraceback(self, *args, **kwargs):
        if not hasattr(sys, 'last_type'):
            return

        if sys.last_type == NameError:  # 90% of the time I mistyped something
            sys.stderr.write("NameError")
            return
        if sys.last_type == AttributeError:
            sys.stderr.write("AttributeError")
            return

        return self.interactive_console.showtraceback()

    def begin(self):
        """The superclass already defined initialize and a few other methods.

        So let's go with begin since we don't have much room in this namespace.
        """
        if self.config is None:
            self.config = Config()
        self.init_profile_dir()
        # self.init_displayhook()

    # def init_displayhook(self):
    # sys.displayhook = RichPromptDisplayHook(shell=InteractiveShellABC)

    def run(self, code_to_run=None):
        if code_to_run is None:
            return

        if code_to_run in sys.modules:
            return runpy.run_module(code_to_run)

        elif Path(code_to_run).resolve().exists():
            runpy.run_path(code_to_run)
        else:
            self.run_line_magic("run", code_to_run)

    def highlight(self, code):
        return pygments.highlight(code, self.lexer, self.formatter, outfile=sys.stderr)

    def write(self, data, *args, **kwargs):
        self.interactive_console.write(self.highlight(data))

    def create_kb(self):
        self.kb = load_key_bindings()

    def create_completer(self):
        self.Completer = rlcompleter.Completer

    @staticmethod
    def execfile(fname, user_global=None):
        """Apparently using global raises an error.

        Could've checked it wasn't reserved I  guess.
        """
        user_global = user_global or globals()
        with open(fname, "rb") as f:
            code_obj = compile(f.read(), "<string>", "exec")
            clean_ns = {}
            # Are you still allowed to do this?
            # return exec(code_obj in clean_ns)
            # nope
            return exec(code_obj, user_global, clean_ns)

    def create_profile_dir(self, profile_dir=None):
        """Modify this so we have a none argument for profile_dir."""
        if profile_dir is not None:
            self.profile_dir = profile_dir
            return
        try:
            self.profile_dir = ProfileDir.create_profile_dir_by_name(
                self.ipython_dir, "default"
            )
        except ProfileDirError:
            self.log.error("Profiledirerror")
        except TraitError:
            self.log.warn("Error")
        except Exception as e:
            self.log.exception(e)

    def showsyntaxerror(self, filename=None, *args, **kwargs):
        """Display the syntax error that just occurred.

        How refreshing is it to not have tracebacks intertwined with
        every other aspect of your application :D

        Parameters
        ----------
        filename :
        **kwargs :

        """
        print('SyntaxError')

    def _showsyntaxerror(self, *args, **kwargs):
        # Override for avoid using sys.excepthook PY-12600
        exception_type, value, tb = sys.exc_info()
        sys.last_type = exception_type
        sys.last_value = value
        sys.last_traceback = tb
        if tb is None:
            return
        if filename and exception_type is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, line) = value.args
            except ValueError:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        formatted = traceback.format_exception_only(exception_type, value)
        sys.stderr.write("".join(formatted))
        return formatted

    def showtraceback(self, *args, **kwargs):
        """Display the exception that just occurred."""
        # Override for avoid using sys.excepthook PY-12600
        try:
            exception_type, value, tb = sys.exc_info()
            sys.last_type = exception_type
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            lines = traceback.format_list(tblist)
            if lines:
                lines.insert(0, "Traceback (most recent call last):\n")
            lines.extend(traceback.format_exception_only(exception_type, value))
        finally:
            tblist = tb = None
        if lines:
            sys.stderr.write("".join(lines))

    def create_custom_toolbar(self) -> HTML:
        """TODO: I want this to return as the bottom toolbar.

        Does it go in self.extra_prompt_options?
        """
        s = "New Terminal REPL"

        @functools.wraps
        def entry(k: str, v: str) -> str:
            return f' | <b><style bg="ansiblue">{k.capitalize()}</style></b> {v}'

        s += entry("multiline", self.config.multiline)
        s += entry("directory", pathlib.Path().cwd())
        s += entry("style", self.config.highlighting_style)

        return HTML(s)

    def prompt_for_code(self, *args, **kwargs):
        """This needs to be here."""
        return self.run(*args, **kwargs)

    @property
    def _last_execution_result(self):
        return self.shell.last_execution_result

    @property
    def _last_execution_succeeded(self):
        return self.shell.last_execution_succeeded

    @property
    def _execution_info(self):
        return self.last_execution_result.info

    def init_traceback_handlers(self, ignored=None, *args, **kwargs):
        faulthandler.enable()
        cgitb.enable(format="text")
        self.sys_excepthook = cgitb.Hook()


if __name__ == "__main__":
    if not Application.initialized():
        config = Application.instance().config

    trace.Trace()
    unimpaired = TerminallyUnimpaired()
