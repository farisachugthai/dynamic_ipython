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
import subprocess
import sys
import types
from contextlib import ContextDecorator
from subprocess import DEVNULL, PIPE, CalledProcessError, CompletedProcess, Popen
from typing import get_type_hints  # what is this?

from IPython.core.getipython import get_ipython

try:
    import pyfzf
except:
    pyfzf = None
    fufpy = fuf = None
else:
    from pyfzf.pyfzf import FzfPrompt

    fufpy = FzfPrompt()
    fuf = fufpy.prompt


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


# @Executable('fzf')


class FZF:
    """Wrap FZF together."""

    fzf_alias = ""

    def __init__(self, fzf_alias=None, fzf_configs=None, **kwargs):
        self.fzf_alias = fzf_alias or ""
        self.fzf_config = fzf_configs or {}
        self._setup_fzf()

    def __repr__(self):
        return "{}    {}".format(self.__class__.__name__, self.fzf_alias)

    def __call__(self, *args, **kwargs):
        """Run :attr:`safe_default_cmd` with ``*args`` as a command.

        Accepts any optional ``**kwargs`` passed along to :func:`subprocess.run`.
        """
        subprocess.run([self.safe_default_cmd, *args], **kwargs)

    @property
    def default_cmds(self):
        return (
            "rg --pretty --hidden --max-columns-preview --no-heading --no-messages --no-column --no-line-number -C 0 -e ^ | fzf --ansi --multi ",
        )

    @property
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

    @property
    def safe_default_cmd(self):
        return shlex.split(shlex.quote(self.default_cmd_str))

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


def busybox_hack(shell):
    # HACK: dear god it feels horrible doing this but shit it works
    from default_profile.startup import aliases_mod

    shell.alias_manager.user_aliases += aliases_mod.LinuxAliases().busybox()
    shell.alias_manager.init_aliases()
    shoddy_hack_for_aliases = [
        ("l", "ls -CF --hide=NTUSER.* --color=always %l"),
        ("la", "ls -AF --hide=NTUSER.* --color=always %l"),
        ("ldir", "ls -Apo --hide=NTUSER.*  --color=always %l | grep /$"),
        # ('lf' ,     'ls -Fo --color=always | grep ^-'),
        # ('ll' ,          'ls -AFho --color=always %l'),
        ("ls", "ls -F --hide=NTUSER.* --color=always %l"),
        ("lr", "ls -AgFhtr --hide=NTUSER.*  --color=always %l"),
        ("lt", "ls -AgFht --hide=NTUSER.* --color=always %l"),
        ("lx", "ls -Fo --hide=NTUSER.* --color=always | grep ^-..x"),
        # ('ldir' ,               'ls -Fhpo | grep /$ %l'),
        ("lf", "ls -Foh --hide=NTUSER.* --color=always | grep ^- %l"),
        ("ll", "ls -AgFh --hide=NTUSER.* --color=always %l"),
        # ('lt' ,          'ls -Altc --color=always %l'),
        # ('lr' ,         'ls -Altcr --color=always %l')
    ]
    for i in shoddy_hack_for_aliases:
        shell.alias_manager.define_alias(*i)


def main():
    """Adding fzf.

    >>> from collections import deque
    >>> user_aliases = deque()
    >>> user_aliases = [('rg', 'rg --hidden --no-messages %l')]

    """
    shell = get_ipython()
    if shell is not None:
        if sys.platform == "win32":
            try:
                from default_profile.startup import aliases_mod
            except ImportError:
                pass
            else:
                busybox_hack(shell)

        fzf_aliases = FZF._setup_fzf()
        shell.alias_manager.define_alias("fzf", "fzf-tmux")
        # default_command = fzf_aliases.default_cmds
        # os.environ.setdefault("FZF_DEFAULT_COMMAND", default_command)


if __name__ == "__main__":
    main()
    if fuf is not None:

        class Fuf(FZF, FzfPrompt):
            fzf_default_opts = None
