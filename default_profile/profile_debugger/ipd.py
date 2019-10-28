#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run ipdb and capture args.

Oct 06, 2019:

    Works as expected!!!

    Start IPython and run this as a post-mortem debugger!


"""
import sys
import traceback
# import signal
from pdb import Pdb

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import PygmentsTokens
# from prompt_toolkit.contrib.completers.system import SystemCompleter
from prompt_toolkit.shortcuts.prompt import PromptSession
from pygments.token import Token

from IPython import get_ipython
# from IPython.core.magics import MagicsClass, cell_magics, line_magics
from IPython.core.completer import IPCompleter
from IPython.core.error import UsageError
# As a heads up I think the super() call goes to Pdb not TerminalPdb.
# from IPython.core.debugger import Pdb
# from IPython.core.interactiveshell import InteractiveShell
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.interactiveshell import TerminalInteractiveShell
# from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.ptutils import IPythonPTCompleter
from IPython.terminal.shortcuts import create_ipython_shortcuts


class IPD(Pdb):
    """Set up the IPython Debugger.

    Rewrote this largely to break up the :meth:`pt_init` from
    `IPython.terminal.debugger.TerminalPdb`.

    """

    def __init__(self, shell=None, keys=None, completer=None, prompt_toolkit_application=None, *args, **kwargs):
        """Add everything to call signature.

        The original only displays star args and star kwargs.

        Parameters
        ----------
        shell : |ip|
            Global IPython
        completer : optional
            What do we use for completions?
        prompt_toolkit_application : prompt_toolkit.PromptSession, optional
            pt_init parameter

        """
        if shell is not None:
            self.shell = shell
        else:
            self.shell = get_ipython()

        if self.shell is None:
            raise UsageError

        if not keys:
            self.keys = self.initialize_keybindings()
        else:
            self.keys = keys

        if completer is None:
            self.completer = self.initialize_completer()
        else:
            self.completer = completer

        self.completer = IPythonPTCompleter(completer, shell=self.shell)

        if prompt_toolkit_application is None:
            self.prompt_toolkit_application = self.pt_init()
        else:
            self.prompt_toolkit_application = prompt_toolkit_application

        super().__init__(self, *args, **kwargs)

    def __repr__(self):
        return '{}\t{}'.format(self.shell, self.completer)

    # TODO:
    # def __call__(self):
    #     initialize()

    def get_prompt_tokens(self):
        """Create the prompt."""
        return [(Token.Prompt, self.prompt)]

    def initialize_completer(self):
        """Create a completion instance for the debugger."""
        return IPCompleter(
            shell=self.shell,
            namespace=self.shell.user_ns,
            global_namespace=globals(),
            parent=self.shell,
        )

    def initialize_keybindings(self):
        """Should make this explicit and as a result independent."""
        return create_ipython_shortcuts(self.shell)

    def pt_init(self):
        """Override the default initialization for prompt_toolkit."""
        return PromptSession(
            message=(lambda: PygmentsTokens(self.get_prompt_tokens())),
            editing_mode=getattr(EditingMode, self.shell.editing_mode.upper()),
            key_bindings=self.keys,
            history=self.shell.debugger_history,
            completer=self.completer,
            enable_history_search=True,
            mouse_support=self.shell.mouse_support,
            complete_style=self.shell.pt_complete_style,
            style=self.shell.style,
            inputhook=self.shell.inputhook,
            color_depth=self.shell.color_depth,
        )


def initialize_ipython():
    """If IPython hasn't been started, then do so.

    #) Build a terminal app in order to force IPython to load the configuration.
    #) Set the trait 'interact' to `False`.
    #) TerminalIPythonApp().initialize([])

    .. todo:: allow for args and kwargs

    """
    # ipapp = TerminalIPythonApp()
    # # Avoid output (banner, prints)
    # ipapp.interact = False
    # # ipapp.initialize([args], kwargs)
    # # I don't know if we can do it that way
    # ip.initialize([])
    # shell = ipapp.shell

    # Unfortunately this doesn't work
    # shell = start_ipython()

    # This creates an IPython instance inside of our debugger
    shell = TerminalInteractiveShell()
    return shell


def is_embedded_shell(shell):
    """Determine if 'shell' is an instance of InteractiveShellEmbed."""
    if isinstance(shell, InteractiveShellEmbed):
        sys.stderr.write(
            "\nYou are currently into an embedded ipython shell,\n"
            "the configuration will not be loaded.\n\n"
        )
        return True


def formatted_traceback():
    # TODO:
    print('Traceback: Extracted stack\n' + repr(traceback.extract_stack()) + '\n')
    print('Traceback: Formatted stack\n' + repr(traceback.format_stack()) + '\n')


def setup_breakpointhook():
    idebug.shell.run_line_magic('debug', '')


def main():
    """Create an instance of our debugger."""
    ip = get_ipython()  # noqa C0103
    if ip is None:  # noqa C0103
        ip = initialize_ipython()

    # with patch_stdout.patch_stdout():
    dynamic_debugger = IPD(shell=ip)
    return dynamic_debugger


if __name__ == "__main__":
    idebug = main()

    if hasattr(sys, 'last_traceback'):
        formatted_traceback()

    sys.breakpointhook = setup_breakpointhook()
    # Vim: set ft=python:
