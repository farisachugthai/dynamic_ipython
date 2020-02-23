#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FZF works in IPython!!!!

Trying to rework this over in ../extensions/namespaces.py

Also worth noting the aliasmanager rewrite in ./22_alias_manager.py

"""
import functools
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
import types

from contextlib import ContextDecorator, contextmanager
from subprocess import DEVNULL, PIPE, CalledProcessError, CompletedProcess, Popen
from typing import get_type_hints, TYPE_CHECKING
from pathlib import Path

try:
    import pyfzf
except:
    pyfzf = None
    fufpy = fuf = None
else:
    from pyfzf.pyfzf import FzfPrompt

    fufpy = FzfPrompt()
    fuf = fufpy.prompt

from prompt_toolkit.application.run_in_terminal import run_in_terminal
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import print_formatted_text as print
from prompt_toolkit.utils import Event

from traitlets.config.application import get_config
from IPython.core.getipython import get_ipython
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.terminal.shortcuts import create_ipython_shortcuts

# try:
#     import pandas as pd
# except ImportError:
#     pd = None

# TODO
# if  TYPE_CHECKING: etc

class Executable(ContextDecorator):
    """An object representing some executable on a user computer."""

    def __init__(self, command):
        """Initialize with *command*."""
        self.command = command
        self.command_path = self._get_command_path()
        super().__init__()

    @property
    def _command(self):
        return self.command

    def _get_command_path(self):
        """Return the path to an executable if *command* is on `PATH`.

        Same signature as :func:`shutil.which`.

        Returns
        -------
        str (path-like)
            Path to an executable if it's found. Otherwise `None`.

        """
        return shutil.which(self.command)

    def __repr__(self):
        return "Executable: {!r}".format(self.command)

    def __call__(self, func, *args, **kwargs):
        if self.command_path is not None:

            @functools.wraps
            def wrapped(*args, **kwargs):
                func(*args, **kwargs)


class RedirectStdout:
    """Need to determine whether to use homebrewed class or contextlib.redirect_stdout."""

    def __init__(self, new_stdout=None):
        """If stdout is None, redirect to /dev/null"""
        self._new_stdout = new_stdout or open(os.devnull, "w")

    def __enter__(self):
        sys.stdout.reconfigure(line_buffering=True)  # implies flush
        self.oldstdout_fno = os.dup(sys.stdout.fileno())
        os.dup2(self._new_stdout.fileno(), 1)

    def __exit__(self, exc_type, exc_value, traceback):
        self._new_stdout.flush()
        os.dup2(self.oldstdout_fno, 1)
        os.close(self.oldstdout_fno)


class FZF:
    """Wrap FZF together."""

    fzf_alias = ""

    def __init__(self, fzf_alias=None, fzf_configs=None, **kwargs):
        self.fzf_alias = fzf_alias or ""
        self.fzf_config = fzf_configs or {}
        self._setup_fzf()
        super().__init__()

    def __repr__(self):
        return "{}    {}".format(self.__class__.__name__, self.fzf_alias)

    def __call__(self, *args, **kwargs):
        """Run :attr:`safe_default_cmd` with ``*args`` as a command.

        Accepts any optional ``**kwargs`` passed along to :func:`subprocess.run`.
        """
        subprocess.run([self.safe_default_cmd, *args], **kwargs)

    def default_cmds(self):
        return "rg --pretty --hidden --max-columns-preview --no-heading --no-messages --no-column --no-line-number -C 0 -e ^ | fzf --ansi --multi "

    def default_cmd(self):
        """Define the cmd for FZF.

        In the sane vein as json.load and json.loads, separate the 2 based on
        the 's'.
        """
        return [
            "rg",
            "--pretty",
            "--hidden",
            "--max-columns-preview",
            "--no-heading",
            "--no-messages",
            "--no-column",
            "--no-line-number",
            "-C",
            "0",
            "-e",
            "^",
            "|",
            "fzf",
            "--ansi",
            "--multi",
        ]

    @contextmanager
    def safe_default_cmd(self):
        return shlex.split(shlex.quote(self.default_cmds()))

    @classmethod
    def _setup_fzf(cls, *args):
        if cls.fzf_alias is None:
            cls.fzf_alias = ()
        if shutil.which("fzf") and shutil.which("rg"):
            # user_aliases.extend(
            #     ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
            cls.fzf_alias = (
                "fzf",
                "rg --pretty --hidden --max-columns-preview --no-heading --no-messages --no-column --no-line-number -C 0 -e ^ | fzf --ansi --multi ",
            )

        elif shutil.which("fzf") and shutil.which("ag"):
            # user_aliases.extend(
            #     ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
            cls.fzf_alias = ("fzf", "ag -C 0 --color-win-ansi --noheading %l | fzf")

        if args:
            cls.fzf_alias.extend(args)

        return cls


def is_tmux():
    """Check if we're using tmux or not."""
    if os.environ.get("TMUX"):
        return True


def is_rg():
    """Returns the path to rg."""
    return shutil.which("rg")

def fzf_history(event):
    if pd is None:
        return
    cnx = sqlite3.connect(home+'/.ipython/profile_default/history.sqlite')
    fzf=FzfPrompt()
    df = pd.read_sql_query("SELECT * FROM history", cnx)
    itext=fzf.prompt(df['source'])
    # print(itext)
    if itext!=[]:
        event.current_buffer.insert_text(itext[0])


def add_fzf_binding():
    insert_mode = ViInsertMode() | EmacsInsertMode()
    registry = get_ipython().pt_app.key_binding

    registry.add_binding(Keys.ControlY,
                         filter=HasFocus(DEFAULT_BUFFER)
                        )(fzf_history)


class TestInter(TerminalInteractiveShell):
    """Checks if IPython is running.

    If not use TerminalIPythonApp().launch_instance to start it.
    Noticed that method while skimming traitlets.config.application.

    """

    def run(self):
        shell = get_ipython()
        if shell is None:
            shell = self.launch_instance()

        config = shell.config


def fzf_keys(inputted_list=None):
    if inputted_list is None:
        inputtted_list = []

    # idk if you can do this.
    with open(tempfile.mkstemp()) as f:
        sys.stdout = f
        sys.stdin = f
        # also is this class a contextmanager because that'd be thoughtful
        FzfPrompt(inputted_list)


def new_shortcuts():
    """Let's overlay a few shortcuts with the default ones."""
    shell = get_ipython()
    kb = create_ipython_shortcuts(shell)
    if hasattr(kb, "add"):
        handle = kb.add
    else:
        # probably should whine
        return

    handle(Keys.ControlT, HasFocus(DEFAULT_BUFFER))(fzf_keys)
    # todo:
    # kb.add_binding()


def run_in_terminal_fzf():
    termshell = TestInter()
    # not sure how pt wants us to do this part
    # TODO:
    # Ah so this raises an error because FzfPrompt() doesn't have an __enter__
    # attribute and we're trying to run it as a contextmanager. ah.
    with run_in_terminal(FzfPrompt(), render_cli_done=True, in_executor=True):
        fzf_prompt = FzfPrompt()
        # launch with
        fzf_prompt.prompt()


if __name__ == "__main__":
    fzf_aliases = FZF._setup_fzf()
    get_ipython().alias_manager.define_alias("fzf", "fzf-tmux")

    home = str(Path.home())

    if fuf is not None:

        class Fuf(FZF, FzfPrompt):
            fzf_default_opts = None
