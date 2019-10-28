#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create OS specific aliases to allow a user to use IPython anywhere."""
import logging
import os
import shutil

from IPython import get_ipython

from default_profile.startup import ask_for_import
# TODO: allow these imports to run and allow fall backs otherwise
from default_profile.util.module_log import stream_logger
from default_profile.util.machine import Platform

ALIAS_LOGGER = stream_logger(
    logger='default_profile.startup.20_aliases',
    msg_format='%(asctime)s : %(levelname)s : %(module)s %(message)s',
    log_level=logging.WARNING)


class LinuxAliases:
    """Add Linux specific aliases.

    Aliases that have either:

        * Only been tested on Linux
        * Only natively exist on Linux
        * Clobber an existing Windows command
            * cmd has a few overlapping commands like :command:`find`
            * powershell intentionally has many aliases that match `busybox`
              aliases, with commands like 'ls' and 'curl' already mapped to
              pwsh builtins.

    Packages such as ConEmu or Cmder allow a large number of GNU/Linux
    built-ins to exist on Windows, and as a result, the list may not be
    comprehensive and it may be that a reasonable
    portion of these aliases can be successfully executed from a shell
    such as Cygwin, Msys2, Mingw, Git on Windows or the Windows
    Subsystem of Linux.

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
        """The WindowsAliases implementation of this is odd so maybe branch off.

        Parameters
        ----------
        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        self.user_aliases = aliases or []
        self.shell = shell or get_ipython()

    def __repr__(self):
        return 'Linux Aliases: {!r}'.format(len(self.user_aliases))

    def busybox(self):
        """Commands that are available on any Unix-ish system.

        Apparently, I don't know how to use classmethods.

        Parameters
        ----------
        None

        Returns
        -------
        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        self.user_aliases += [
            ('cs', 'cd %s && ls -F --color=always %s'),
            ('cp', 'cp -v %l'),  # cp mv mkdir and rmdir are all overridden
            ('df', 'df -ah --total'),
            ('dU', 'du -d 1 -h --apparent-size --all | sort -h | tail -n 10'),
            ('dus', 'du -d 1 -ha %l'),
            ('echo', 'echo -e %l'),
            ('free', 'free -mt'),
            ('gpip',
             'export PIP_REQUIRE_VIRTUALENV=0; python -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null'
             ),
            ('gpip2',
             'export PIP_REQUIRE_VIRTUALENV=0; python2 -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null'
             ),
            ('gpip3',
             'export PIP_REQUIRE_VIRTUALENV=0; python3 -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null'
             ),
            ('head', 'head -n 30 %l'),
            ('l', 'ls -CF --color=always %l'),
            ('la', 'ls -AF --color=always %l'),
            ('ldir', 'ls -Apo --color=always %l | grep /$'),
            # ('lf', 'ls -Fo --color=always | grep ^-'),
            # ('ll', 'ls -AFho --color=always %l'),
            ('ls', 'ls -F --color=always %l'),
            ('lr', 'ls -AgFhtr --color=always %l'),
            ('lt', 'ls -AgFht --color=always %l'),
            ('lx', 'ls -Fo --color=always | grep ^-..x'),
            # ('ldir', 'ls -Fhpo | grep /$ %l'),
            ('lf', 'ls -Foh --color=always | grep ^- %l'),
            ('ll', 'ls -AgFh --color=always %l'),
            # ('lt', 'ls -Altc --color=always %l'),
            # ('lr', 'ls -Altcr --color=always %l'),
            ('mk', 'mkdir -pv %l && cd %l'),  # check if this works. only mkdir
            ('mkdir', 'mkdir -pv %l'),
            ('mv', 'mv -v %l'),
            ('r', 'fc -s'),
            ('redo', 'fc -s'),
            # Less annoying than -i but more safe
            # only prompts with more than 3 files or recursed dirs.
            ('rm', 'rm -Iv %l'),
            ('rmdir', 'rmdir -v %l'),
            ('default_profile',
             'cd ~/projects/dotfiles/unix/.ipython/default_profile'),
            ('startup',
             'cd ~/projects/dotfiles/unix/.ipython/default_profile/startup'),
            ('tail', 'tail -n 30 %l'),
        ]
        return self.user_aliases

    def __iter__(self):
        return self._generator()

    def _generator(self):
        for itm in self.user_aliases:
            yield itm

    def thirdparty(self):
        """Contrasted to busybox, these require external installation.

        As a result it'll be of value to check that they're even in
        the namespace.
        """
        self.user_aliases += [
            ('ag', 'ag --hidden --color --no-column %l'),
            ('nvim', 'nvim %l'),
            ('nman', 'nvim -c "Man %l" -c"wincmd T"'),
            ('tre', 'tree -DAshFC --prune -I .git %l'),
        ]
        return self.user_aliases


class CommonAliases:
    r"""Add aliases common to all OSes. Overwhelmingly :command:`Git` aliases.

    This method adds around 70 to 80 aliases that can be
    implemented on most of the major platforms.

    The only real requirement is Git being installed and working. Docker
    commands possibly going to be added.

    .. todo:: :command:`git show`

    """

    def __init__(self, shell=None, user_aliases=None):
        """OS Agnostic aliases.

        Parameters
        ----------
        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        self.user_aliases = user_aliases or []
        self.shell = shell or get_ipython()

    def __iter__(self):
        return self._generator()

    def _generator(self):
        for itm in self.user_aliases:
            yield itm

    def __repr__(self):
        return 'Common Aliases: {!r}'.format(len(self.user_aliases))

    def unalias(self, alias):
        """Remove an alias.

        .. magic:: unalias

        Parameters
        ----------
        alias : Alias to remove

        """
        self.shell.run_line_magic('unalias', alias)

    def python_exes(self):
        """Python executables like pydoc get executed in a subprocess currently.

        Let's fix that behavior because that's silly.
        """
        self.unalias(pydoc)
        self.unalias(apropos)

        import pydoc
        from pydoc import apropos

    def git(self):
        """100+ git aliases."""
        self.user_aliases += [
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
            ('git hist',
             'git log --pretty="format:%h %ad | %d [%an]" --graph --date=short '
             '--branches --abbrev-commit --oneline %l'),
            ('git last', 'git log -1 HEAD %l'),
            ('git staged', 'git diff --cached %l'),
            ('git rel', 'git rev-parse --show-prefix %l'),
            ('git root', 'git rev-parse --show-toplevel %l'),
            ('git unstage', 'git reset HEAD %l'),
            ('git unstaged', 'git diff %l'),
            ('gl', 'git log %l'),
            ('glo',
             'git log --pretty="format:%h %ad | %d [%an]" --graph --decorate --abbrev-commit --oneline --branches --all %l'
             ),
            ('gls', 'git ls-tree master %l'),
            ('git ls', 'git ls-tree master %l'),
            ('gm', 'git merge --no-ff %l'),
            ('gma', 'git merge --abort %l'),
            ('gmc', 'git merge --continue %l'),
            ('gmm', 'git merge master %l'),
            ('gmt', 'git mergetool %l'),
            ('gp', 'git pull --all %l'),
            ('gpo', 'git pull origin %l'),
            ('gpom', 'git pull origin master %l'),
            ('gpu', 'git push %l'),
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
            ('gshs', 'git stash show --stat %l'),
            ('gshsp', 'git stash show --patch %l'),
            ('gss', 'git status -sb %l'),
            ('gst', 'git diff --stat %l'),
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
        return self.user_aliases


class WindowsAliases:
    """Aggregated Window aliases. Provides simplified system calls for NT.

    Methods
    -------
    Implements aliases specific to cmd or powershell.

    Notes
    -----
    Would it be useful to subclass :class:`reprlib.Repr` here?

    """

    def __init__(self, shell=None, user_aliases=None):
        """Initialize the platform specific alias manager with IPython.

        Parameters
        ----------
        shell : str (external command), optional
            The command used to invoke the system shell. If none
            is provided during instantiation, the function will
            set :attr:`WindowsAliases.shell` to the
            |ip| instance.

        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        self.shell = shell or get_ipython()
        self.user_aliases = user_aliases
        if self.user_aliases is None:
            self.cmd_aliases()

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
        return 'Windows Aliases: {!r}'.format(len(self.user_aliases))

    @classmethod
    def cmd_aliases(cls):
        r"""Aliases for the :command:`cmd` shell.

        .. todo:: Cmd, :envvar:`COPYCMD` and IPython

            Need to consider how to handle env vars. Still working out how
            IPython's logic for Window's shells works, but that'll determine
            how :envvar:`SHELL` and :envvar:`COMSPEC` are handled.

        .. note:: Windows environment variables

            However it'll also take some consideration to figure
            out how to handle env vars like :envvar:`COPYCMD`. Should we
            build them into the aliases we have here because
            that'll affect :data:`_ip.user_aliases.mv`?

        Also note :envvar:`DIRCMD` for :command:`dir`.

        """
        cls.user_aliases = [
            ('cp', 'copy %s %s'),
            ('copy', 'copy %s %s'),
            ('ddir', 'dir /ad /on %l'),
            ('echo', 'echo %l'),
            ('ldir', 'dir /ad /on %l'),
            ('ll', 'dir /Q %l'),
            # I know this really isn't the same but I need it
            ('ln', 'mklink %s %s'),
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


def main():
    """Set up aliases for the user namespace for IPython.

    Planning on coming up with a new way of introducing the aliases into the user namespace.

    """
    if not hasattr(_ip, 'magics_manager'):
        raise Exception('Are you running in IPython?')

    common = CommonAliases()

    machine = Platform()
    # TODO: Work in the Executable() class check.
    user_aliases = common.git()

    if machine.is_linux:
        # user_aliases += LinuxAliases().busybox()
        linux_aliases = LinuxAliases()
        user_aliases.extend(linux_aliases.busybox())

    elif machine.is_win:
        # finish the shell class in default_profile.util.machine
        # then we can create a shell class that determines if
        # we're in cmd or pwsh
        user_aliases += WindowsAliases().cmd_aliases()

    _ip.alias_manager.user_aliases = user_aliases
    # Apparently the big part i was missing was rerunning the init_aliases method
    _ip.alias_manager.init_aliases()

    ALIAS_LOGGER.info('Number of aliases is: %s' % user_aliases)


if __name__ == "__main__":
    _ip = get_ipython()

    if _ip is not None:
        main()
