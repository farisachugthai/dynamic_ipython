#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File for all shell aliases.

===============
IPython Aliases
===============

.. module:: aliases
    :synopsis: Create aliases for :mod:`IPython` to ease use as a system shell.

.. rubric:: Changelog - Mar 03, 2019

    Moved git aliases into new :func:`common_aliases()`

.. versionchanged:: May 18, 2019

    IPython might've deprecated |ip| function
    :func:`MagicsManager.define_alias` and replaced it with
    :func:`MagicsManager.register_alias`

Overview
========

This module utilizes `_ip`, the global :mod:`IPython` |ip|
instance, and fills the ``user_ns`` with common Linux idioms.


Parameters
==========

When writing aliases, an ``%alias`` definition can take various string
placeholders. As per the official documentation:


.. topic:: ``%l`` parameter

    You can use the ``%l`` specifier in an ``%alias`` definition to represent the
    whole line when the alias is called.

Meaning that it behaves similarly to the parameter ``$*`` in shells like eshell.

The documentation goes on to say:

.. ipython::

    In [2]: %alias bracket echo "Input in brackets: <%l>"
    In [3]: bracket hello world
    Input in brackets: <hello world>

Note that we quote when in the configuration file but when running alias
interactively the syntax ``%alias alias_name cmd`` doesn't require quoting.


Attributes
==========

_ip : |ip|
    A global object representing the active IPython session.
    Contains varying packages as well as the current global namespace.
    Doesn't need to be defined in advance during an interactive session.


Examples
========

This code creates a handful of platform-specific functions where each
returns :ref:`user_aliases`. Realizing that this is also used in the
:mod:`IPython.core.alias` implementation, the source code of the
implementation has been provided for reference.

.. ipython:: python

    class AliasManager(Configurable):

        default_aliases = List(default_aliases()).tag(config=True)
        user_aliases = List(default_value=[]).tag(config=True)
        shell = Instance('IPython.core.interactiveshell.InteractiveShellABC', allow_none=True)

        def __init__(self, shell=None, **kwargs):
            super(AliasManager, self).__init__(shell=shell, **kwargs)
            # For convenient access
            self.linemagics = self.shell.magics_manager.magics['line']
            self.init_aliases()


See Also
========

:mod:`IPython.core.alias`
    Aliases file for IPython.


Yet to be implemented
=====================

- ``ssh-day``
- ``extract``
- :command:`fzf` in its many invocations.
- A function that wraps around :func:|ip|`.MagicsManager.define_alias()` and
  checks for whether the executable is on the :envvar:`PATH` all in one swoop.

"""
import logging
from shutil import which

from IPython import get_ipython
from IPython.core.alias import AliasError
from profile_default.util import module_log
from profile_default.util.machine import Platform

LOGGER = module_log.stream_logger(
    logger=logging.getLogger(name=__name__),
    msg_format='%(asctime)s : %(levelname)s : %(module)s %(message)s',
    log_level=logging.INFO)


def linux_specific_aliases(_ip=None):
    r"""Add Linux specific aliases.

    Aliases that have either:

        * Only been tested on Linux
        * Only natively exist on Linux
        * Clobber an existing Windows command (cmd in particular)

    Convenience packages exist such as ConEmu or Cmder which allow a large
    number of GNU/Linux built-ins to exist on Windows, and as a result, this
    list may not be comprehensive.

    Parameters
    ----------
    _ip : |ip|
        The global instance of :mod:`IPython`.


    Below is the source code for the function that is invoked here.

    .. if the undefined self.shell kills things then just don't make this
    .. an executable code block

    .. code-block:: python3

        def define_alias(self, name, cmd):
            # Define a new alias after validating it.
            # This will raise an :exc:`AliasError` if there are validation
            # problems.
            caller = Alias(shell=self.shell, name=name, cmd=cmd)
            self.shell.magics_manager.register_function(caller, magic_kind='line',
            magic_name=name)

    Returns
    -------
    _ip.user_aliases : list of ('alias', 'system command') tuples

    """
    _user_aliases = [
        ('ag', 'ag --hidden --color --no-column %l'),
        ('cs', 'cd %s && ls -F --color=always %s'),
        ('cp', 'cp -iv %l'),  # cp mv mkdir and rmdir are all overridden
        ('dus', 'du -d 1 -ha %l'),
        ('echo', 'echo -e %l'),
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
        ('la', 'ls -AF --color=always %l'),
        ('l', 'ls -CF --color=always %l'),
        ('ll', 'ls -AlF --color=always %l'),
        ('ls', 'ls -F --color=always %l'),
        ('lt', 'ls -Altcr --color=always %l'),
        ('mk', 'mkdir -pv %l && cd %l'),  # check if this works. only mkdir
        ('mkdir', 'mkdir -pv %l'),
        ('mv', 'mv -iv %l'),
        ('nman', 'nvim -c "Man %l" -c"wincmd T"'),
        ('r', 'fc -s'),
        ('redo', 'fc -s'),
        ('rm', 'rm -v %l'),
        ('rmdir', 'rmdir -v %l'),
        ('profile_default',
         'cd ~/projects/dotfiles/unix/.ipython/profile_default'),
        ('startup',
         'cd ~/projects/dotfiles/unix/.ipython/profile_default/startup'),
        ('tail', 'tail -n 30 %l'),
        ('tre', 'tree -ashFC -I .git -I __pycache__ --filelimit 25'),
    ]
    return _user_aliases


def common_aliases(_ip=None):
    r"""Add aliases common to all OSes. Overwhelmingly :command:`Git` aliases.

    This method adds around 70 to 80 aliases that can be implemented on most
    of the major platforms.

    The only real requirement is Git being installed and working.

    .. todo:: :command:`git show`

    Parameters
    ----------
    _ip : |ip|
        The global instance of IPython.


    Returns
    -------
    _ip.user_aliases : List of tuples
        User aliases.
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
        ('gcim', 'git commit --verbose --message %l'),   # TODO: what's the other parameter we can give?
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
        ('gl', 'git log %l'),
        ('glo',
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


def cmd_aliases(_ip=None):
    r"""Aliases for the cmd interpreter specifically.

    .. todo::

        Do a :envvar:`COMSPEC` check.

    """
    _ip.user_aliases = [
        ('copy', 'copy'),
        ('ddir', 'dir /ad /on'),
        ('ldir', 'dir /ad /on'),
        ('mklink', 'mklink'),
        ('move', 'move'),
        ('mv', 'move'),
        ('ren', 'ren'),
        ('rmdir', 'rmdir'),
    ]
    return _ip.user_aliases


def windows_aliases(_ip=None):
    r"""Aliases for Windows OSes.

    Has only been tested on Windows 10 in a heavily configured environment.

    Niceties such as Git for Windows, ag-silversearcher, ripgrep,
    ConEmu and others have been added.

    The minimum number of assumptions possible have been made; however, note
    that this section is still under development and frequently changes.

    .. warning:: Warning: 5 aliases have been commented out as they emit warnings
                 upon being set. They're unfortunately aliases to cmd commands
                 and as a result don't run correctly in PowerShell...

    .. note::

        The environment variable :envvar:`COMSPEC` is checked to determine the
        default shell and it is assumed the user is running IPython from there
        which may not always be true.

    .. code-block:: powershell

        Alias           % -> ForEach-Object
        Alias           ? -> Where-Object
        Alias           clhy -> Clear-History
        Alias           cli -> Clear-Item
        Alias           clp -> Clear-ItemProperty
        Alias           cls -> Clear-Host
        Alias           clv -> Clear-Variable
        Alias           cnsn -> Connect-PSSession
        Alias           compare -> Compare-Object
        Alias           cpi -> Copy-Item
        Alias           cpp -> Copy-ItemProperty
        Alias           curl -> Invoke-WebRequest
        Alias           cvpa -> Convert-Path
        Alias           dbp -> Disable-PSBreakpoint
        Alias           diff -> Compare-Object
        Alias           dnsn -> Disconnect-PSSession
        Alias           ebp -> Enable-PSBreakpoint
        Alias           epal -> Export-Alias
        Alias           epcsv -> Export-Csv
        Alias           epsn -> Export-PSSession
        Alias           erase -> Remove-Item
        Alias           etsn -> Enter-PSSession
        Alias           exsn -> Exit-PSSession
        Alias           fc -> Format-Custom
        Alias           fl -> Format-List
        Alias           foreach -> ForEach-Object
        Alias           ft -> Format-Table
        Alias           fw -> Format-Wide
        Alias           gal -> Get-Alias
        Alias           gbp -> Get-PSBreakpoint
        Alias           gc -> Get-Content
        Alias           gci -> Get-ChildItem
        Alias           gcm -> Get-Command
        Alias           gcs -> Get-PSCallStack
        Alias           gdr -> Get-PSDrive
        Alias           ghy -> Get-History
        Alias           gi -> Get-Item
        Alias           gjb -> Get-Job
        Alias           gl -> Get-Location
        Alias           gm -> Get-Member
        Alias           gmo -> Get-Module
        Alias           gp -> Get-ItemProperty
        Alias           gps -> Get-Process
        Alias           gpv -> Get-ItemPropertyValue
        Alias           group -> Group-Object
        Alias           gsn -> Get-PSSession
        Alias           gsnp -> Get-PSSnapin
        Alias           gsv -> Get-Service
        Alias           gu -> Get-Unique
        Alias           gv -> Get-Variable
        Alias           gwmi -> Get-WmiObject
        Alias           h -> Get-History
        Alias           icm -> Invoke-Command
        Alias           iex -> Invoke-Expression
        Alias           ihy -> Invoke-History
        Alias           ii -> Invoke-Item
        Alias           ipal -> Import-Alias
        Alias           ipcsv -> Import-Csv
        Alias           ipmo -> Import-Module
        Alias           ipsn -> Import-PSSession
        Alias           irm -> Invoke-RestMethod
        Alias           ise -> powershell_ise.exe
        Alias           iwmi -> Invoke-WMIMethod
        Alias           iwr -> Invoke-WebRequest
        Alias           lp -> Out-Printer
        Alias           man -> help
        Alias           md -> mkdir
        Alias           measure -> Measure-Object
        Alias           mi -> Move-Item
        Alias           mount -> New-PSDrive
        Alias           mp -> Move-ItemProperty
        Alias           nal -> New-Alias
        Alias           ndr -> New-PSDrive
        Alias           ni -> New-Item
        Alias           nmo -> New-Module
        Alias           npssc -> New-PSSessionConfigurationFile
        Alias           nsn -> New-PSSession
        Alias           nv -> New-Variable
        Alias           ogv -> Out-GridView
        Alias           oh -> Out-Host
        Alias           r -> Invoke-History
        Alias           rbp -> Remove-PSBreakpoint
        Alias           rcjb -> Receive-Job
        Alias           rcsn -> Receive-PSSession
        Alias           rd -> Remove-Item
        Alias           rdr -> Remove-PSDrive
        Alias           ri -> Remove-Item
        Alias           rjb -> Remove-Job
        Alias           rmo -> Remove-Module
        Alias           rni -> Rename-Item
        Alias           rnp -> Rename-ItemProperty

    That's some non-trivial stuff right there! First try on all 4 of them!

    """
    _ip.user_aliases = [
        ('ac', 'Add-Content %l'),
        ('asnp', 'Add-PSSnapin %l'),
        ('cat', 'Get-Content %l'),
        # ('cd', 'Set-Location %l'),
        ('clc', 'Clear-Content %l'),
        ('clear', 'Clear-History %l'),
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
    return _ip.user_aliases


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
    if which('fzf') and which('rg'):
        user_aliases.extend(
            ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
    elif which('fzf') and which('ag'):
        user_aliases.extend(
            ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))

    return user_aliases


def main():
    """Set up aliases for the user namespace for IPython."""
    _ip = get_ipython()

    # if not isinstance(_ip, IPython.terminal.interactiveshell.InteractiveShell):
    #     raise Exception('Are you running in IPython?')
    # so let's not do isinstance. embrace the interface not the type!
    if not hasattr(_ip, 'magics_manager'):
        raise Exception('Are you running in IPython?')

    user_aliases = []

    machine = Platform('.')

    if machine.is_linux:

        # Now let's get the Linux aliases
        user_aliases += linux_specific_aliases(_ip)
        # LOGGER.info("The number of available aliases after linux aliases"
        # " is: " + str(len(user_aliases)))

    elif machine.is_conemu:  # should check for 'nix-tools as an env var
        user_aliases += windows_aliases(_ip)

    user_aliases += common_aliases(_ip)

    __setup_fzf(user_aliases)

    # LOGGER.info("The number of available user aliases is: "
    #"" + str(len(user_aliases)))

    for i in user_aliases:
        try:
            _ip.alias_manager.define_alias(i[0], i[1])
        except AliasError as e:
            LOGGER.error(e)


if __name__ == "__main__":
    main()
