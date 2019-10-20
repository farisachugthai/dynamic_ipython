#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import shutil


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


def setup_fzf(user_aliases):
    """Needs a good deal of work.

    On second thought this function has some potential. Or at least it
    jogged a thought in my brain.

    A good idea would be to make a function that's implemented as a decorator,
    so we'll need to import functools.wrapped, and have that decorator run
    shutil.which on an external command. If it exists continue with the
    function and alias it. If it doesn't, then return None.

    This function was useful for pointing out that the decorator should allow
    for multiple arguments.

    """
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
