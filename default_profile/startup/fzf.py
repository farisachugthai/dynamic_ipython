#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FZF works in IPython!!!!"""
import functools
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import types

from contextlib import ContextDecorator, contextmanager
from subprocess import DEVNULL, PIPE, CalledProcessError, CompletedProcess, Popen
from typing import get_type_hints, TYPE_CHECKING
from pathlib import Path

try:
    import pyfzf
except:
    pyfzf = None
    fufpy = fuf = FzfPrompt = None
else:
    from pyfzf.pyfzf import FzfPrompt

    fufpy = FzfPrompt()
    fuf = fufpy.prompt

from prompt_toolkit.application.run_in_terminal import run_in_terminal
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode, EmacsInsertMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import print_formatted_text as print
from prompt_toolkit.utils import Event

from IPython.core.getipython import get_ipython


@contextmanager
def inside_dir(dirpath):
    """Context manager that executes code from inside the given directory.

    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


def run_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the exit status.

    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(
            shlex.split(shlex.quote(command)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def check_output_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the command output.

    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_output(
            shlex.split(shlex.quote(command)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


class Executable(ContextDecorator):
    """An object representing some executable on a user computer."""

    def __init__(self, command):
        """Initialize with *command*."""
        self.command = command
        self.command_path = self._get_command_path(command)
        super().__init__()

    @property
    def _command(self):
        return self.command

    def _get_command_path(self, command):
        """Return the path to an executable if *command* is on `PATH`.

        Same signature as :func:`shutil.which`.

        Returns
        -------
        str (path-like)
            Path to an executable if it's found. Otherwise `None`.

        """
        return shutil.which(command)

    def __repr__(self):
        return "Executable: {!r}".format(self.command)

    def __call__(self, func, *args, **kwargs):
        if self.command_path is not None:

            @functools.wraps
            def wrapped(*args, **kwargs):
                func(*args, **kwargs)


class FZF:
    """Wrap FZF together."""

    def __init__(self, fzf_configs=None, **kwargs):
        self.fzf_config = fzf_configs or {}
        self._setup_fzf()
        super().__init__()

    def __repr__(self):
        return "{}    {}".format(self.__class__.__name__, self.fzf_config)

    def __call__(self, *args, **kwargs):
        """Run :attr:`safe_default_cmd` with ``*args`` as a command.

        Accepts any optional ``**kwargs`` passed along to :func:`subprocess.run`.
        """
        with (RedirectStdout(), "rt+") as f:
            return subprocess.run(
                [self.safe_default_cmd, *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **kwargs
            )

    def run(self, *args, **kwargs):
        print("Running: {}".format(self.safe_default_cmd))
        return subprocess.run(
            [self.safe_default_cmd, *args],
            **kwargs,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def default_cmds(self):
        return (
            "rg --pretty --hidden --max-columns-preview --no-heading"
            "--no-messages --no-column --no-line-number -C 0 -e ^ "
            "| fzf --ansi --multi "
        )

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
        if shutil.which("fzf") and shutil.which("rg"):
            cls.fzf = (
                "fzf",
                "rg --pretty --hidden --max-columns-preview --no-heading"
                "--no-messages --no-column --no-line-number -C 0 -e ^ "
                "| fzf --ansi --multi ",
            )

        elif shutil.which("fzf") and shutil.which("ag"):
            cls.fzf = ("fzf", "ag -C 0 --color-win-ansi --noheading %l | fzf")

        if args:
            cls.fzf.extend(args)

        return cls


def is_tmux():
    """Check if we're using tmux or not."""
    if os.environ.get("TMUX"):
        return True


def is_rg():
    """Returns the path to rg."""
    return shutil.which("rg")


def fzf_history(event):
    try:
        import pandas as pd
    except ImportError:
        return
    if pd is None:
        return
    cnx = sqlite3.connect(home + "/.ipython/profile_default/history.sqlite")
    fzf = FzfPrompt()
    df = pd.read_sql_query("SELECT * FROM history", cnx)
    itext = fzf.prompt(df["source"])
    if itext != []:
        event.current_buffer.insert_text(itext[0])


def add_fzf_binding():
    insert_mode = ViInsertMode() | EmacsInsertMode()
    registry = get_ipython().pt_app.key_bindings

    handle = registry.add_binding
    handle(Keys.ControlY, filter=HasFocus(DEFAULT_BUFFER))(fzf_history)
    # this freezes the whole prompt holy hell
    # handle(Keys.ControlT, filter=HasFocus(DEFAULT_BUFFER))(fzf_keys)


def fzf_keys(inputted_list=None):

    if inputted_list is None:
        inputted_list = []

    # idk if you can do this.
    with open(tempfile.mkstemp()[-1], "rt+") as f:
        sys.stdout = f
        sys.stdin = f
        # also is this class a contextmanager because that'd be thoughtful
        FzfPrompt(inputted_list)


def run_in_terminal_fzf():
    # not sure how pt wants us to do this part
    # TODO:
    # Ah so this raises an error because FzfPrompt() doesn't have an __enter__
    # attribute and we're trying to run it as a contextmanager. ah.
    with run_in_terminal(FZF(), render_cli_done=True, in_executor=True):
        fzf_prompt = FzfPrompt()
        # launch with
        fzf_prompt.prompt()


def fgs():
    """Return git status!"""
    cmd = ["bash", "-c", 'source "$HOME/.bashrc.d/fzf_git.bash"\nfgh\n']
    try:
        ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        ret = 1
    return ret


def fzf_history(event):
    cnx = sqlite3.connect(home + "/.ipython/profile_default/history.sqlite")
    fzf = FzfPrompt()
    df = pd.read_sql_query("SELECT * FROM history", cnx)
    itext = fzf.prompt(df["source"])
    # print(itext)
    if itext != []:
        event.current_buffer.insert_text(itext[0])


if __name__ == "__main__":
    fzf_aliases = FZF._setup_fzf()
    get_ipython().alias_manager.define_alias("fzf", "fzf-tmux")

    home = str(Path.home())

    if fuf is not None:

        class Fuf(FZF, FzfPrompt):
            fzf_default_opts = None
