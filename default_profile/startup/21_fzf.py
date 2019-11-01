#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        return 'Executable: {!r}'.format(self.command)

    @functools.wraps
    def __call__(self, func, *args, **kwargs):
        """Make the class a callable.

        I think shutil.which() returns either a `str` or `None`.

        So we could just check that if self.command_path is not None: return func

        Probably would be faster. *shrugs*.

        """
        if os.path.exists(self.command_path):
            def wrapped(*args, **kwargs):
                func(*args, **kwargs)


def setup_fzf(user_aliases=None):
    if user_aliases is None:
        user_aliases = []
    if shutil.which('fzf') and shutil.which('rg'):
        # user_aliases.extend(
        #     ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
        user_aliases.extend((
            'fzf',
            'rg --pretty --hidden --max-columns=300 --max-columns-preview '
            '.*[a-zA-Z]* --no-heading -m=30 --no-messages --color=ansi --no-column '
            ' --no-line-number -C 0 | fzf --ansi'))

    elif shutil.which('fzf') and shutil.which('ag'):
        # user_aliases.extend(
        #     ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
        user_aliases.extend(
            ('fzf', 'ag -C 0 --color-win-ansi --noheading | fzf --ansi'))

    return user_aliases


def is_fzf_tmux():
    """Check if we're using tmux or not."""
    if os.environ.get('TMUX'):
        return True


def add_rg():
    """Returns the path to rg."""
    return shutil.which('rg')


def busybox_hack():
    # HACK: dear god it feels horrible doing this but shit it works
    shell.alias_manager.user_aliases += aliases_mod.LinuxAliases().busybox()
    shell.alias_manager.init_aliases()

# @Executable(fzf_tmux())
# def add_fzf_alias():


if __name__ == "__main__":
    if sys.platform == 'win32':
        shell = get_ipython()
        try:
            from default_profile.startup import aliases_mod
        except ImportError:
            pass
        else:
            busybox_hack()
