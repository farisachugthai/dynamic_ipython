#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FZF works in IPython!!!!

Note
-----
Trying to rework this over in ../extensions/namespaces.py

"""
import functools
import os
import shutil
import sys

from IPython import get_ipython


class Executable:
    """An object representing some executable on a user computer."""

    def __init__(self, command):
        """Initialize with *command*."""
        self.command = command
        self.command_path = self._get_command_path()

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

    @functools.wraps
    def __call__(self, func, *args, **kwargs):
        if self.command_path is not None:

            def wrapped(*args, **kwargs):
                func(*args, **kwargs)


def setup_fzf(fzf_alias=None):
    if fzf_alias is None:
        fzf_alias = ()
    if shutil.which("fzf") and shutil.which("rg"):
        # user_aliases.extend(
        #     ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
        fzf_alias = (
            "fzf",
            "rg --pretty --hidden --max-columns-preview --no-heading --no-messages --no-column -C 0 -e ^ | fzf --ansi --multi",
        )

    elif shutil.which("fzf") and shutil.which("ag"):
        # user_aliases.extend(
        #     ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
        fzf_alias = ("fzf", "ag -C 0 --color-win-ansi --noheading %l | fzf -")

    return fzf_alias


# def is_fzf_tmux():
# def fzf_tmux():
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


# @Executable(fzf_tmux())
# def add_fzf_alias():


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

        shell.alias_manager.user_aliases.append(setup_fzf())
        shell.alias_manager.init_aliases()


if __name__ == "__main__":
    main()
