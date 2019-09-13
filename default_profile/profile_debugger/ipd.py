#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Vim: set ft=python:
"""Run ipdb and capture args.

Currently crashing on IPD.pt_init line with IPCompleter.

Can we implement differently?
"""
import signal
import sys

from IPython import get_ipython
# from IPython.core.magics import MagicsClass, cell_magics, line_magics
from IPython.core.completer import IPCompleter
from IPython.core.debugger import Pdb
# from IPython.core.interactiveshell import InteractiveShell
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.debugger import TerminalPdb
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.ptutils import IPythonPTCompleter
from IPython.terminal.shortcuts import suspend_to_bg, cursor_in_leading_ws, create_ipython_shortcuts

from prompt_toolkit import patch_stdout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.contrib.completers.system import SystemCompleter
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import (Condition, has_focus, has_selection,
    vi_insert_mode, emacs_insert_mode)
from prompt_toolkit.key_binding.bindings.completion import display_completions_like_readline
from prompt_toolkit.shortcuts.prompt import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import PygmentsTokens

from pygments.token import Token


class IPD(TerminalPdb):
    """Set up the IPython Debugger."""


    def __init__(self, shell=None, change_keys=False, _ptcomp=None, *args, **kwargs):
        """Add everything to call signature."""
        self._ptcomp = _ptcomp
        self.shell = shell
        self.change_keys = change_keys
        self.pt_init(change_keys)
        super().__init__(self, color_scheme=shell.style, *args, **kwargs)

    def pt_init(self, change_keys=False):
        """Override the default initialization for prompt_toolkit."""
        pass
        def get_prompt_tokens():
            return [(Token.Prompt, self.prompt)]

        if self._ptcomp is None:
            compl = IPCompleter(shell=self.shell,
                                        namespace={},
                                        global_namespace={},
                                        parent=self.shell,
                                       )
            self._ptcomp = IPythonPTCompleter(compl)

        kb = KeyBindings()
        if change_keys:
            supports_suspend = Condition(lambda: hasattr(signal, 'SIGTSTP'))
            kb.add('c-z', filter=supports_suspend)(suspend_to_bg)

            if self.shell.display_completions == 'readlinelike':
                kb.add('tab', filter=(has_focus(DEFAULT_BUFFER)
                                      & ~has_selection
                                      & vi_insert_mode | emacs_insert_mode
                                      & ~cursor_in_leading_ws
                                  ))(display_completions_like_readline)
        else:
            kb = create_ipython_shortcuts()

        self.pt_app = PromptSession(
                            message=(lambda: PygmentsTokens(get_prompt_tokens())),
                            editing_mode=getattr(EditingMode, self.shell.editing_mode.upper()),
                            key_bindings=kb,
                            history=self.shell.debugger_history,
                            completer=self._ptcomp,
                            enable_history_search=True,
                            mouse_support=self.shell.mouse_support,
                            complete_style=self.shell.pt_complete_style,
                            style=self.shell.style,
                            inputhook=self.shell.inputhook,
                            color_depth=self.shell.color_depth,
        )


def idbg(_ptcomp=None, args=None, kwargs=None):
    """Create our debugger."""
    IPD(_ptcomp, args, kwargs)


def idebug():
    """Set up the IPython debugger."""
    try:
        import ipdb
    except (ImportError, ModuleNotFoundError):
        # Execute the beginning of ipdb's __main__ mod.
        try:
            from IPython import get_ipython
        except (ImportError, ModuleNotFoundError):
            sys.exit('Neither ipython nor ipdb installed. Use pdb.')
        else:
            shell = get_ipython()

        if shell is None:
            # Not inside IPython
            # Build a terminal app in order to force ipython to load the
            # configuration
            ipapp = TerminalIPythonApp()
            # Avoid output (banner, prints)
            ipapp.interact = False
            ipapp.initialize([])
            shell = ipapp.shell
        else:
            # Running inside IPython

            # Detect if embed shell or not and display a message
            if isinstance(shell, InteractiveShellEmbed):
                sys.stderr.write(
                    "\nYou are currently into an embedded ipython shell,\n"
                    "the configuration will not be loaded.\n\n"
                )
    else:
        ipdb.run(str(sys.argv[1:]))


if __name__ == "__main__":
    args = sys.argv[:]

    ip = get_ipython()
    if ip is not None:
        if len(args) > 0:
            _ptcomp = args[0]
        else:
            _ptcomp = None

        with patch_stdout.patch_stdout():
            idbg(_ptcomp, args)
    else:
        idebug()
