#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run pdb and capture args.

Oct 06, 2019:

    Works as expected!!!

    Start IPython and run this as a post-mortem debugger!

Unrelated but who wants to see something I was surprised about.::

    from bdb import foo, bar

Yeah those are real functions.::

    foo()

"""
import pdb
from pdb import Pdb
import sys
import traceback

from prompt_toolkit.completion import DynamicCompleter
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.shortcuts.prompt import PromptSession

from pygments.token import Token

from IPython import get_ipython

# from IPython.core.completer import IPCompleter
from IPython.core.error import UsageError
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.terminal.ptutils import IPythonPTCompleter
from IPython.terminal.shortcuts import create_ipython_shortcuts


class IPD(Pdb):
    """Set up the IPython Debugger.

    Rewrote this largely to break up the :meth:`pt_init` from
    `IPython.terminal.debugger.TerminalPdb` and decouple it from the rest
    of the application.
    """

    def __init__(
        self,
        shell=None,
        keys=None,
        context=None,
        *args,
        **kwargs
    ):
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
        self.shell = shell or get_ipython()

        if self.shell is None:
            raise UsageError

        self.keys = self.initialize_keybindings(keys)
        # self.completer = completer or self.initialize_completer()
        self.completer = DynamicCompleter(self.initialize_completer())

        self.prompt = "Your Debugger: "
        self.context = context
        self.pt_session = self.pt_init()

        super().__init__(self, *args, **kwargs)

    def __repr__(self):
        return f"{self.prompt}"

    # TODO:
    # def __call__(self):
    #     initialize()

    def get_prompt_tokens(self):
        """Create the prompt."""
        return [(Token.Prompt, self.prompt)]

    def initialize_completer(self):
        """Create a completion instance for the debugger."""
        return IPythonPTCompleter(
            shell=self.shell,
            # namespace=self.shell.user_ns,
            # global_namespace=globals(),
            # parent=self.shell,
        )

    def initialize_keybindings(self, custom_keys=None):
        _ = [load_key_bindings(), create_ipython_shortcuts(self.shell), ]
        if custom_keys is None:
            return merge_key_bindings(_)
        else:
            return merge_key_bindings(_.append(custom_keys))

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
            # style=self.shell.style,
            # inputhook=self.shell.inputhook,
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
    """Allow a little post mortem introspection."""
    print("Traceback: Extracted stack\n" + repr(traceback.extract_stack()) + "\n")
    print("Traceback: Formatted stack\n" + repr(traceback.format_stack()) + "\n")


def init_debugger():
    """Create an instance of our debugger."""
    ip = get_ipython()  # noqa C0103
    if ip is None:  # noqa C0103
        ip = initialize_ipython()

    if hasattr(sys, "last_traceback"):
        formatted_traceback()
    else:
        pdb.set_trace()

    # with patch_stdout.patch_stdout():
    dynamic_debugger = IPD(shell=ip)
    return dynamic_debugger


if __name__ == "__main__":
    debugger = init_debugger()
    try:
        debugger.pt_session.prompt()
    except (KeyboardInterrupt, EOFError):
        sys.exit("Bye!")
