#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===============
IPython Aliases
===============
.. module:: 20_aliases
    :synopsis: Set up additional alias managers and add user_aliases to the namespace.

Refactoring TODO:

Create a class with instance attributes for `sys.platform`.
Break linux up like so::

    class AliasOSAgnostic:

        def __init__(self):
            self._sys.platform = sys.platform().lower()

        @property
        def has_alias(self):
            return ....

    class LinuxAlias(AliasOSAgnostic):

        def busybox(self):
            aliases = [
                ('cd', 'cd foo %l'),
                ...
                ('ls', 'ls -F --color=always %l)
            ]

        def standardubuntu(self):
            aliases = [
                ('ag', 'ag -l %l')
                ('rg', 'way too many options')
            ]

Then maybe implement either a factory function or a factory manager but I haven't
fleshed that part out in my head.

This may have to take the backburner as I reorganize the rest of the repo.

If you're breaking up Linux functionality, may I recommend the following man
page to reference?


BASH-BUILTINS(7)          Miscellaneous Information Manual          BASH-BUILTINS(7)

NAME
       bash-builtins - bash built-in commands, see bash(1)

SYNOPSIS
       bash defines the following built-in commands: :, ., [, alias, bg, bind,
       break, builtin, case, cd, command, compgen, complete, continue,
       declare, dirs, disown, echo, enable, eval, exec, exit, export, fc, fg,
       getopts, hash, help, history, if, jobs, kill, let, local, logout, popd,
       printf, pushd, pwd, read, readonly, return, set, shift, shopt, source,
       suspend, test, times, trap, type, typeset, ulimit, umask, unalias,
       unset, until, wait, while.


I think that :command:`declare -f` could have a nice tie in to inspect.is_function()
or whatever.

"""
import logging
import os
import shutil


from IPython import get_ipython
from IPython.core.alias import AliasError, AliasManager
from IPython.core.error import UsageError

from default_profile.util import module_log
from default_profile.util.machine import Platform

LOGGER = module_log.stream_logger(
    logger='default_profile.startup.20_aliases',
    msg_format='%(asctime)s : %(levelname)s : %(module)s %(message)s',
    log_level=logging.INFO
)


class Executable:
    """An object representing some executable on a user computer."""

    def __init__(self, command):
        """Initialize with 'command'."""
        self.command = command

    def runs(self):
        """Check for the executability of a system command.

        Same signature as :func:`shutil.which`.
        """
        return shutil.which(self.command)


class LinuxAliases:
    """Add Linux specific aliases.

    Aliases that have either:

        * Only been tested on Linux
        * Only natively exist on Linux
        * Clobber an existing Windows command (cmd in particular)

    Convenience packages exist such as ConEmu or Cmder which allow a large
    number of GNU/Linux built-ins to exist on Windows, and as a result, this
    list may not be comprehensive.

    Below is the source code for the function
    :func:`IPython.core.magics.define_alias()` that is invoked here.::

        def define_alias(self, name, cmd):
            # Define a new alias after validating it.
            # This will raise an :exc:`AliasError` if there are validation
            # problems.
            caller = Alias(shell=self.shell, name=name, cmd=cmd)
            self.shell.magics_manager.register_function(caller, magic_kind='line',
            magic_name=name)

    """

    def __init__(self, shell=None, aliases=None):
        """The WindowsAliases implementation of this is odd so maybe branch off."""
        self.aliases = aliases
        self.shell = shell or get_ipython()

    def __repr__(self):
        return 'Linux Aliases: {!r}'.format(
            len(self.shell.alias_manager.aliases)
        )

    @classmethod
    def busybox(cls):
        """Commands that are available on any Unix-ish system.

        Parameters
        ----------
        None

        Returns
        -------
        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        _user_aliases = [
            ('cs', 'cd %s && ls -F --color=always %s'),
            ('cp', 'cp -v %l'),  # cp mv mkdir and rmdir are all overridden
            ('dus', 'du -d 1 -ha %l'),
            ('echo', 'echo -e %l'),
            (
                'gpip',
                'export PIP_REQUIRE_VIRTUALENV=0; python -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null'
            ),
            (
                'gpip2',
                'export PIP_REQUIRE_VIRTUALENV=0; python2 -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null'
            ),
            (
                'gpip3',
                'export PIP_REQUIRE_VIRTUALENV=0; python3 -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null'
            ),
            ('head', 'head -n 30 %l'),
            ('l', 'ls -CF --color=always %l'),
            ('la', 'ls -AF --color=always %l'),
            ('ldir', 'ls -Fhpo | grep /$ %l'),
            ('lf', 'ls -Foh | grep ^- %l'),
            ('ll', 'ls -AgFh --color=always %l'),
            ('ls', 'ls -Fh --color=always %l'),
            ('lt', 'ls -Altc --color=always %l'),
            ('lr', 'ls -Altcr --color=always %l'),
            ('mk', 'mkdir -pv %l && cd %l'),  # check if this works. only mkdir
            ('mkdir', 'mkdir -pv %l'),
            ('mv', 'mv -v %l'),
            ('r', 'fc -s'),
            ('redo', 'fc -s'),
            ('rm', 'rm -v %l'),
            ('rmdir', 'rmdir -v %l'),
            (
                'default_profile',
                'cd ~/projects/dotfiles/unix/.ipython/default_profile'
            ),
            (
                'startup',
                'cd ~/projects/dotfiles/unix/.ipython/default_profile/startup'
            ),
            ('tail', 'tail -n 30 %l'),
        ]
        return _user_aliases

    def __iter__(self):
        return self._generator()

    def _generator(self):
        for itm in self.items():
            yield itm

    def thirdparty(self):
        """Contrasted to busybox, these require external installation.

        As a result it'll be of value to check that they're even in the namespace.
        """
        user_aliases = [
            ('ag', 'ag --hidden --color --no-column %l'),
            ('nman', 'nvim -c "Man %l" -c"wincmd T"'),
            ('tre', 'tree -ashFC -I .git -I __pycache__ --filelimit 25'),
        ]


def common_aliases():
    r"""Add aliases common to all OSes. Overwhelmingly :command:`Git` aliases.

    This method adds around 70 to 80 aliases that can be implemented on most
    of the major platforms.

    The only real requirement is Git being installed and working. Docker
    commands possibly going to be added.

    .. todo:: :command:`git show`

    """
    _user_aliases = [
        ('g', 'git diff --staged --stat %l'),
        ('ga', 'git add %l'),
        ('gaa', 'git add --all %l'),
        ('gai', 'git add --interactive %l'),
        ('gap', 'git add --patch %l'),
        ('gar', 'git add --renormalize -A %l'),
        ('gau', 'git add --update %l'),
        ('ga.', 'git add .'),
        ('gb', 'git branch --all %l'),
        ('gbl', 'git blame %l'),
        ('gbr', 'git branch %l'),
        ('gbru', 'git branch --set-upstream-to origin %l'),
        ('gbrv', 'git branch --all --verbose %l'),
        ('gci', 'git commit %l'),
        ('gcia', 'git commit --amend %l'),
        ('gciad', 'git commit --amend --date=%l'),
        ('gcid', 'git commit --date=%l'),
        ('gcim', 'git commit --verbose --message %s'),
        ('gcl', 'git clone %l'),
        ('gcls', 'git clone --depth 1 %l'),
        ('gco', 'git checkout %l'),
        ('gcob', 'git checkout -b %l'),
        ('gd', 'git diff %l'),
        ('gds', 'git diff --staged %l'),
        ('gds2', 'git diff --staged --stat %l'),
        ('gdt', 'git difftool %l'),
        ('gdw', 'git diff --word-diff %l'),
        ('gf', 'git fetch --all %l'),
        ('gfe', 'git fetch %l'),
        ('ggc', 'git gc %l'),
        ('ggcp', 'git gc --prune %l'),
        ('git', 'git %l'),
        (
            'git hist',
            'git log --pretty="format:%h %ad | %d [%an]" --graph --date=short '
            '--branches --abbrev-commit --oneline %l'
        ),
        ('git last', 'git log -1 HEAD %l'),
        ('gl', 'git log %l'),
        (
            'glo',
            'git log --graph --decorate --abbrev-commit --oneline --branches --all'
        ),
        ('gls', 'git ls-tree master %l'),
        ('git ls', 'git ls-tree master %l'),
        ('gm', 'git merge --no-ff %l'),
        ('gma', 'git merge --abort %l'),
        ('gmc', 'git merge --continue %l'),
        ('gmm', 'git merge master %l'),
        ('gmt', 'git mergetool %l'),
        ('gp', 'git pull --all'),
        ('gpo', 'git pull origin'),
        ('gpom', 'git pull origin master'),
        ('gpu', 'git push'),
        ('gr', 'git remote -v %l'),
        ('gre', 'git remote %l'),
        ('grb', 'git rebase %l'),
        ('grba', 'git rebase --abort %l'),
        ('grbc', 'git rebase --continue %l'),
        ('grbi', 'git rebase --interactive %l'),
        ('gs', 'git status %l'),
        ('gsh', 'git stash %l'),
        ('gsha', 'git stash apply %l'),
        ('gshc', 'git stash clear %l'),
        ('gshd', 'git stash drop %l'),
        ('gshl', 'git stash list %l'),
        ('gshp', 'git stash pop %l'),
        ('gshs', 'git stash show %l'),
        ('gshsp', 'git stash show --patch %l'),
        ('gss', 'git status -sb %l'),
        ('gst', 'git diff --stat %l'),
        ('git staged', 'git diff --cached %l'),
        ('git rel', 'git rev-parse --show-prefix %l'),
        ('git root', 'git rev-parse --show-toplevel %l'),
        ('git unstage', 'git reset HEAD %l'),
        ('git unstaged', 'git diff %l'),
        ('gt', 'git tag --list %l'),
        ('lswitch', 'legit switch'),
        ('lsync', 'legit sync'),
        ('lpublish', 'legit publish'),
        ('lunpublish', 'legit unpublish'),
        ('lundo', 'legit undo'),
        ('lbranches', 'legit branches'),
        ('ssh-day', 'eval "$(ssh-agent -s)"; ssh-add %l'),
        ('xx', 'quit'),  # this is a sweet one
        ('..', 'cd ..'),
        ('...', 'cd ../..'),
    ]
    return _user_aliases


class WindowsAliases:
    """Aggregated Window aliases. Provides simplified system calls for NT.

    Methods
    -------
    Implements aliases specific to cmd or powershell.

    Notes
    -----
    Would it be useful to subclass :class:`enum.Enum` here?

    """

    def __init__(self, shell=None):
        """Initialize the platform specific alias manager with IPython.

        Parameters
        ----------
        shell : external command, optional
            The command used to invoke the system shell. If none is provided
            during instantiation, the function will set :attr:`WindowsAliases.shell`
            to the |ip| instance.

        """
        self.shell = shell or get_ipython()

    @staticmethod
    def _find_exe(self, exe=None):
        """Use :func:`shutil.which` to determine whether an executable exists.

        Parameters
        ----------
        exe : command, optional
            The command to check.

        Returns
        -------
        path : str (path-like)
            Where the executable is located.

        """
        return shutil.which(exe) or None

    def __repr__(self):
        return 'Windows Aliases: {!r}'.format(
            len(self.shell.alias_manager.aliases)
        )

    @classmethod
    def cmd_aliases(cls):
        r"""Aliases for the :command:`cmd` shell.

        .. todo:: Cmd, :envvar:`COPYCMD` and IPython

            Need to consider how to handle env vars. Still working out how
            IPython's logic for Window's shells works, but that'll determine
            how :envvar:`SHELL` and :envvar:`COMSPEC` are handled.

            However it'll also take some consideration to figure out how to
            handle env vars like COPYCMD. Should we build them into the aliases
            we have here because that'll affect :data:`_ip.user_aliases.mv`?

            Also note DIRCMD for :command:`dir`.
        """
        cls.user_aliases = [
            ('cp', 'copy %s %s'),
            ('copy', 'copy %s %s'),
            ('ddir', 'dir /ad /on %l'),
            ('ldir', 'dir /ad /on %l'),
            ('ll', 'dir /Q %l'),
            ('ln', 'mklink %s %s'
             ),  # I know this really isn't the same but I need it
            ('make', 'make.bat %l'),  # Useful when we're building docs
            ('mklink', 'mklink %s %s'),
            ('move', 'move %s %s'),
            ('mv', 'move %s %s'),
            ('ren', 'ren'),
            ('rmdir', 'rmdir %l'),
        ]
        return cls.user_aliases

    @classmethod
    def powershell_aliases(cls):
        r"""Aliases for Windows OSes using :command:`powershell`.

        Has only been tested on Windows 10 in a heavily configured environment.

        Niceties such as Git for Windows, ag-silversearcher, ripgrep,
        ConEmu and others have been added.

        The minimum number of assumptions possible have been made; however, note
        that this section is still under development and frequently changes.
        """
        cls.user_aliases = [
            ('ac', 'Add-Content %l'),
            ('asnp', 'Add-PSSnapin %l'),
            ('cat', 'Get-Content %l'),
            # ('cd', 'Set-Location %l'),
            ('clc', 'Clear-Content %l'),
            # ('clear', 'Clear-History %l'),
            ('conda env', 'Get-Conda-Environment %l'),
            ('copy', 'Copy-Item %l'),
            ('cp', 'Copy-Item %l'),
            ('del', 'Remove-Item %l'),
            ('dir', 'Get-ChildItem %l'),
            ('echo', 'Write-Output %l'),
            # ('history', 'Get-History %l'),
            ('kill', 'Stop-Process'),
            ('l', 'Get-ChildItem %l'),
            ('ll', 'GetChildItem -Verbose %l'),
            ('ls', 'Get-ChildItem %l'),
            ('man', 'Get-Help %l'),
            ('md', 'mkdir %l'),
            ('move', 'Move-Item %l'),
            ('mv', 'Move-Item %l'),
            # ('popd', 'Pop-Location %l'),
            ('pro', 'nvim $Profile.CurrentUserAllHosts'),
            ('ps', 'Get-Process %l'),
            # ('pushd', 'Push-Location %l'),
            # ('pwd', 'Get-Location %l'),
            ('ren', 'Rename-Item %l'),
            ('rm', 'Remove-Item %l'),
            ('rmdir', 'Remove-Item %l'),
            ('rp', 'Remove-ItemProperty %l'),
            ('rsn', 'Remove-PSSession %l'),
            ('rv', 'Remove-Variable %l'),
            ('rvpa', 'Resolve-Path %l'),
            ('sajb', 'Start-Job %l'),
            ('sal', 'Set-Alias %l'),
            ('saps', 'Start-Process %l'),
            ('sasv', 'Start-Service %l'),
            ('sbp', 'Set-PSBreakpoint %l'),
            ('select', 'Select-Object %l'),
            ('set', 'Set-Variable %l'),
            ('si', 'Set-Item %l'),
            ('sl', 'Set-Location %l'),
            ('sleep', 'Start-Sleep %l'),
            ('sls', 'Select-String %l'),
            ('sort', 'Sort-Object %l'),
            ('sp', 'Set-ItemProperty %l'),
            ('spjb', 'Stop-Job %l'),
            ('spps', 'Stop-Process %l'),
            ('spsv', 'Stop-Service %l'),
            ('start', 'Start-Process %l'),
            ('stz', 'Set-TimeZone %l'),
            ('sv', 'Set-Variable %l'),
            ('tee', 'Tee-Object %l'),
            (
                'tree',
                'tree /F /A %l',
            ),
            ('type', 'Get-Content %l'),
            ('where', 'Where-Object %l'),
            ('wjb', 'Wait-Job %l'),
            ('write', 'Write-Output %l'),
        ]
        return cls.user_aliases

    def user_shell(self):
        """Determine the user's shell. Checks :envvar:`SHELL` and :envvar:`COMSPEC`."""
        if self.shell:
            return self.shell
        elif os.environ.get('SHELL'):
            return os.environ.get('SHELL')
        elif os.environ.get('COMSPEC'):
            return os.environ.get('COMSPEC')
        else:
            raise


def __setup_fzf(user_aliases):
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
            ' --no-line-number -C 0 | fzf --ansi'
        ))

    elif shutil.which('fzf') and shutil.which('ag'):
        # user_aliases.extend(
        #     ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
        user_aliases.extend(
            ('fzf', 'ag -C 0 --color-win-ansi --noheading | fzf --ansi')
        )

    return user_aliases


def main():
    """Set up aliases for the user namespace for IPython.

    Planning on coming up with a new way of introducing the aliases into the user namespace.

    """
    if not hasattr(_ip, 'magics_manager'):
        raise Exception('Are you running in IPython?')

    user_aliases = common_aliases()
    machine = Platform()

    if machine.is_linux:
        user_aliases += LinuxAliases().busybox()
    elif machine.is_win:
        # finish the shell class in default_profile.util.machine
        # then we can create a shell class that determines if
        # we're in cmd or pwsh
        # win_ = WindowsAliases(_ip)
        # if win
        user_aliases += WindowsAliases().cmd_aliases()

    _ip.alias_manager.user_aliases = user_aliases
    # Apparently the big part i was missing was rerunning the init_aliases method
    _ip.alias_manager.init_aliases()

    LOGGER.debug('Number of aliases is: %s' % user_aliases)


if __name__ == "__main__":
    _ip = get_ipython()

    if _ip is not None:
        main()
