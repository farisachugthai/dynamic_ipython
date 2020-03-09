#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create OS specific aliases to allow a user to use IPython anywhere.

Properly map aliases as dictionaries.
As stated in the language reference under Common Sequence Operations.:

.. compound::

    Concatenating immutable sequences always results in a new object.
    This means that building up a sequence by repeated concatenation
    will have a quadratic runtime cost in the total sequence length.
    To get a linear runtime cost, you must switch to one of the
    alternatives below:

        - **If concatenating tuple objects, extend a list instead.**

"""
import keyword
import logging
import operator
import os
import platform
import shutil
import subprocess
import traceback
from collections import UserDict
from typing import Iterable, TYPE_CHECKING, Dict

from IPython.core.alias import default_aliases
from IPython.core.getipython import get_ipython
from traitlets.config.application import ApplicationError


class AliasError(Exception):
    pass


class InvalidAliasError(AliasError):
    pass


def validate_alias(alias) -> Dict:
    try:
        caller = self.shell.magics_manager.magics["line"][self.name]
    except KeyError:
        pass
    else:
        if not isinstance(caller, Alias):
            raise InvalidAliasError(
                "The name %s can't be aliased "
                "because it is another magic command." % self.name
            )

    if not (isinstance(self.cmd, str)):
        raise InvalidAliasError(
            "An alias command must be a string, " "got: %r" % self.cmd
        )

    nargs = self.cmd.count("%s") - self.cmd.count("%%s")

    if (nargs > 0) and (self.cmd.find("%l") >= 0):
        raise InvalidAliasError(
            "The %s and %l specifiers are mutually " "exclusive in alias definitions."
        )

    return nargs


class Alias(UserDict):
    """Callable object storing the details of one alias.

    Reasonably this is the object that should be the UserDict. CommonAliases
    makes more sense as a list of dicts.
    """

    def __init__(self, name, cmd):
        """Validate the alias, and return the number of arguments."""
        self.name = name
        self.cmd = cmd
        if self.name in self.blacklist:
            # Wait can we note that we didn't checkout the keyword list though.
            raise InvalidAliasError(
                f"The name {self.name} can't be aliased because it is a keyword or builtin."
            )

    @property
    def shell(self):
        return get_ipython()

    @property
    def blacklist(self):
        """Override the super classes blacklist. The reset magic no longer works.

        We change prompt_toolkit properties and don't reset them with that magic,
        so it expects the interface to continue existing.

        """
        blacklist = ["dhist", "alias", "unalias"]
        blacklist.extend(keyword.kwlist)
        return blacklist

    def __repr__(self):
        return f"<Alias: {self.name!r} for {self.cmd!r}>"

    def __call__(self, rest=""):
        """If an Alias is called, run it with the shell's system function.

        Parameters
        ----------
        rest : str
            Remainder of the user's command line.

        """
        cmd = self.cmd
        nargs = self.nargs
        # Expand the %l special to be the user's input line
        if cmd.find("%l") >= 0:
            cmd = cmd.replace("%l", rest)
            rest = ""

        if nargs == 0:
            if cmd.find("%%s") >= 1:
                cmd = cmd.replace("%%s", "%s")
            # Simple, argument-less aliases
            cmd = "%s %s" % (cmd, rest)
        else:
            # Handle aliases with positional arguments
            args = rest.split(None, nargs)
            if len(args) < nargs:
                raise UsageError(
                    "Alias <%s> requires %s arguments, %s given."
                    % (self.name, nargs, len(args))
                )
            cmd = "%s %s" % (cmd % tuple(args[:nargs]), " ".join(args[nargs:]))

        self.shell.system(cmd)


class CommonAliases(UserDict):
    r"""Aliases that are usable on any major platform.

    Aliases are added by calling the :meth:`update` method which will add
    aliases to the attribute *dict_aliases*.

    In addition, note that the definition for updating indicates that the
    class `update`\s aliases and will `add` other instances.

    """

    shell = get_ipython()

    def __init__(self, user_aliases=None, **kwargs):
        """OS Agnostic aliases.

        Parameters
        ----------
        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        if user_aliases is None:
            self.user_aliases = default_aliases()
        else:
            self.user_aliases = user_aliases
        self.git()
        self.dict_aliases = self.tuple_to_dict(self.user_aliases)
        self.python_exes()
        # if kwargs is not None:
        # surprisingly that doesnt work
        if len(kwargs) != 0:
            self.update(**kwargs)
        super().__init__(self.dict_aliases)

    @property
    def alias_manager(self):
        """The 'alias_manager' attribute of |ip|."""
        return self.shell.alias_manager

    def define_alias(self, name, cmd):
        """Define a new alias.

        Examples
        --------
        ::

            In [54]: pkg?
            Repr: <alias pkg for 'pkg'>
            In [55]: aliases + ('pkg', 'pkg list-a')
            In [56]: pkg?
            Repr: <alias pkg for 'pkg list-a'>

        """
        caller = Alias(shell=self.shell, name=name, cmd=cmd)
        try:
            self.shell.magics_manager.register_function(
                caller, magic_kind="line", magic_name=name
            )
        except AliasError:
            return

    def is_alias(self, name):
        return name in self.dict_aliases

    def soft_define_alias(self, name, cmd):
        """Define a new alias and don't raise an error on an invalid alias.

        """
        self.alias_manager.soft_define_alias(name, cmd)

    def undefine_alias(self, name):
        """Override to raise AliasError not ValueError.

        We're not subclassing AliasManager here but still attempting to
        match it's interface.
        """
        if self.is_alias(name):
            del self.linemagics[name]
        else:
            raise AliasError("%s is not an alias" % name)

    def __repr__(self):  # reprlib?
        return "<Common Aliases>: # of aliases: {!r} ".format(len(self.dict_aliases))

    def update(self, other):
        """Update the mapping of aliases to system commands.

        Ensure that this is properly defined as this can be critical for speed.


        If a TypeError is raised by doing so then attempt to pass the alias along
        to the shell's `AliasManager` with `soft_define_alias`.
        """
        try:
            self.dict_aliases.update(other)
        except TypeError:
            self.soft_define_alias(alias)

    def __copy__(self):
        return copy.copy(self.aliases)

    def __contains__(self, other):
        return other in self.dict_aliases

    def __iter__(self):
        return iter(self.dict_aliases.items())

    def __add__(self, other, name=None, cmd=None, *args):
        """Allow instances to be added."""
        if hasattr(other, "dict_aliases"):
            self.update(other.dict_aliases)
        if name is None and cmd is None:
            if len(args) == 2:
                name, cmd = args
            else:
                name, cmd = other
        self.define_alias(name, cmd)

    def __mul__(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.dict_aliases)

    def __next__(self):
        max = len(self)
        if max >= self.idx:
            # Reset the loop and raise stopiteration
            self.idx = 0
            raise StopIteration
        self.idx += 1
        return self.dict_aliases[self.idx]

    def __getitem__(self, index):
        return operator.getitem(self.kb.bindings, index)

    def len(self):
        return self.__len__()

    def add(self, aliases):
        for i in aliases:
            self.__add__(i)

    # def __getattr__(self, attr):
    #     return getattr(self, attr)

    def tuple_to_dict(self, list_of_tuples):
        a = list_of_tuples
        if a is None:
            a = self.user_aliases
        ret = {}
        for i, j in enumerate(a):
            ret[a[i][0]] = a[i][1]

        return ret

    def unalias(self, alias):
        """Remove an alias."""
        self.shell.run_line_magic("unalias", alias)

    def user_shell(self):
        """Determine the user's shell. Checks :envvar:`SHELL` and :envvar:`COMSPEC`."""
        if self.shell:
            return self.shell
        elif os.environ.get("SHELL"):
            return os.environ.get("SHELL")
        elif os.environ.get("COMSPEC"):
            return os.environ.get("COMSPEC")
        else:
            raise OSError(
                "Neither $SHELL nor $COMSPEC set. Can't determine running terminal."
            )

    def python_exes(self):
        """Python executables like pydoc get executed in a subprocess currently.

        Let's fix that behavior because that's silly.

        So this method may have exposed a big problem in the way these data
        structures are set up. It'd be way smarter to have this set up like
        dictionaries.

        I want to do a check for if pydoc and apropos are in teh aliases.
        But if we iterate over the list then we still get a tuple.
        We could do something like::

            for i in self.user_aliases:
                if i[0] == 'pydoc':
                    self.unalias('pydoc')

        But that's clunky because we're forced to iterate over all aliases.
        Then we could try and do something like a merge sort to find pydoc
        and apropos quickly but jeez that's gonna get complicated kinda quick
        don't you think?

        .. todo::
            os.environ => env

        """
        if "pydoc" in self.dict_aliases.keys():
            self.unalias("pydoc")
            import pydoc
        if "apropos" in self.dict_aliases.keys():
            self.unalias("apropos")
            from pydoc import apropos
        if "which" in self.dict_aliases.keys():
            self.unalias("which")
            from shutil import which
        if "chown" in self.dict_aliases.keys():
            self.unalias("chown")
            from shutil import chown

    def git(self):
        self.user_aliases += [
            ("g", "git diff --staged --stat %l"),
            ("ga", "git add -v %l"),
            ("gaa", "git add --all %l"),
            ("gai", "git add --interactive %l"),
            ("gap", "git add --patch %l"),
            ("gar", "git add --renormalize %l"),
            ("gau", "git add --update %l"),
            ("ga.", "git add ."),
            ("gb", "git branch -avv %l"),
            ("gbl", "git blame %l"),
            ("gbr", "git branch %l"),
            ("gbrd", "git branch -d %l"),
            ("gbrD", "git branch -D %l"),
            ("gbrrd", "git branch -rd %l"),
            ("gbrrD", "git branch -rD %l"),
            ("gbru", "git branch --set-upstream-to --verbose origin %l"),
            ("gbrv", "git branch --all --verbose --remote %l"),
            ("gci", "git commit %l"),
            ("gcia", "git commit --amend %l"),
            ("gciad", "git commit --amend --date=%l"),
            ("gcid", "git commit --date=%l"),
            ("gcim", "git commit --verbose --message %s"),
            ("gcl", "git clone --progress %l"),
            (
                "gcls",
                "git clone --progress --depth 1 --single-branch --branch master %s",
            ),
            ("gco", "git checkout %l"),
            ("gcob", "git checkout -b %l"),
            ("gd", "git diff %l"),
            ("gds", "git diff --staged %l"),
            ("gds2", "git diff --staged --stat %l"),
            ("gdt", "git difftool %l"),
            ("gdw", "git diff --word-diff %l"),
            ("gf", "git fetch --all %l"),
            ("gfe", "git fetch %l"),
            ("ggc", "git gc %l"),
            ("ggcp", "git gc --prune %l"),
            ("git", "git %l"),
            ("git_config_list", "git config --get --global %l"),
            ("git_config_glob", "git config --get-regex --global %l.*"),
            # If you're on a topic branch, shows commit msgs since split
            ("git_fork", "git show-branch --current %l"),
            (
                "git_hist",
                'git log --pretty="format:%h %ad | %d [%an]" --graph --date=short '
                "--branches --abbrev-commit --oneline %l",
            ),
            ("git_last_msg", "git log -1 HEAD -- ."),
            ("git_last_patch", "git show --source"),
            ("git_staged", "git diff --cached %l"),
            ("git_rel", "git rev-parse --show-prefix %l"),
            ("git_root", "git rev-parse --show-toplevel %l"),
            ("git_unstage", "git reset HEAD %l"),
            ("git_unstaged", "git diff %l"),
            (
                "gl",
                'git log --pretty=format:"%Cred%h%Creset %C(yellow)%d%Creset %Cgreen(%cr) %C(bold blue)<%an>%Creset" --all --abbrev-commit --abbrev=7 --date=relative --graph --decorate %l',
            ),
            #  gl with a message
            (
                "glg",
                r'git log --pretty=format:"%Cred%h%Creset -%C(yellow)%d%Creset%Cwhite %Cgreen(%cr) %C(bold blue)<%an>%Creset" --all --abbrev-commit --date=relative',
            ),
            ("glo", "git log %l"),
            (
                "glog",
                'git log --pretty="format:%h %ad | %d [%an]" --graph --decorate --abbrev-commit --oneline --branches %l',
            ),
            ("gls", "git ls-tree master %l"),
            ("git ls", "git ls-tree master %l"),
            ("gm", "git merge --stat --squash --progress %l"),
            ("gma", "git merge --abort %l"),
            ("gmc", "git merge --continue %l"),
            ("gmm", "git merge --stat --squash --progress master %l"),
            ("gmt", "git mergetool %l"),
            ("gp", "git pull --all %l"),
            ("gpo", "git pull origin %l"),
            ("gpom", "git pull origin master %l"),
            ("gpu", "git push %l"),
            ("gpuf", "git push --force $args"),
            ("gpuo", "git push origin $args"),
            ("gpuof", "git push origin --force $args"),
            ("gr", "git remote -v %l"),
            ("grb", "git rebase %l"),
            ("grba", "git rebase --abort %l"),
            ("grbc", "git rebase --continue %l"),
            ("grbi", "git rebase --interactive %l"),
            ("gre", "git remote %l"),
            ("gs", "git status %l"),
            ("gsb", "git status -sb %l"),
            ("gsh", "git stash %l"),
            ("gsha", "git stash apply %l"),
            ("gshc", "git stash clear %l"),
            ("gshd", "git stash drop %l"),
            ("gshl", "git stash list %l"),
            ("gshp", "git stash pop %l"),
            ("gshs", "git stash show --stat %l"),
            ("gshsp", "git stash show --patch %l"),
            ("gss", "git status -sb %l"),
            ("gst", "git diff --stat %l"),
            ("gsw", "git switch --progress %l"),
            ("gswm", "git switch --progress master %l"),
            ("gt", "git tag --list %l"),
            ("gtd", "git tag --delete %l"),
            ("ssh-day", 'eval "$(ssh-agent -s)"; ssh-add %l'),
            ("xx", "quit"),  # this is a sweet one
            ("..", "cd .."),
            ("...", "cd ../.."),
        ]

    def ls_patch(self, shell):
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
            try:
                shell.alias_manager.define_alias(*i)
            except InvalidAliasError:
                raise


class LinuxAliases(CommonAliases):
    """Add Linux specific aliases."""

    def __repr__(self):
        return "Linux Aliases: {!r}".format(len(self.user_aliases))

    def busybox(self):
        """Commands that are available on any Unix-ish system.

        Apparently, I don't know how to use classmethods.

        Returns
        -------
        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        self.user_aliases += [
            ("cs", "cd %s && ls -F --color=always %s"),
            ("cp", "cp -v %l"),  # cp mv mkdir and rmdir are all overridden
            ("df", "df -ah --total"),
            ("dU", "du -d 1 -h --apparent-size --all | sort -h | tail -n 10"),
            ("dus", "du -d 1 -ha %l"),
            ("echo", "echo -e %l"),
            ("free", "free -mt"),
            (
                "gpip",
                "export PIP_REQUIRE_VIRTUALENV=0; python -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null",
            ),
            (
                "gpip2",
                "export PIP_REQUIRE_VIRTUALENV=0; python2 -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null",
            ),
            (
                "gpip3",
                "export PIP_REQUIRE_VIRTUALENV=0; python3 -m pip %l; export PIP_REQUIRE_VIRTUALENV=1 > /dev/null",
            ),
            ("head", "head -n 30 %l"),
            ("l", "ls -CF --color=always %l"),
            ("la", "ls -AFh --color=always %l"),
            ("ldir", "ls -Fhpo --color=always %l | grep /$"),
            ("lf", "ls -Foh --color=always | grep ^-"),
            ("ll", "ls -FAgh --color=always %l"),
            ("ls", "ls -Fh --color=always %l"),
            # alternatively -Altcr
            ("lr", "ls -AgFhtr --color=always %l"),
            # alternatively could do ls -Altc
            ("lt", "ls -AgFht --color=always %l"),
            ("lx", "ls -Fo --color=always | grep ^-..x"),
            ("mk", "mkdir -pv %l && cd %l"),  # check if this works. only mkdir
            ("mkdir", "mkdir -pv %l"),
            ("mv", "mv -v %l"),
            ("r", "fc -s"),
            ("redo", "fc -s"),
            # Less annoying than -i but more safe
            # only prompts with more than 3 files or recursed dirs.
            ("rm", "rm -Iv %l"),
            ("rmdir", "rmdir -v %l"),
            ("default_profile", "cd ~/projects/dotfiles/unix/.ipython/default_profile"),
            ("startup", "cd ~/projects/dotfiles/unix/.ipython/default_profile/startup"),
            ("tail", "tail -n 30 %l"),
        ]

    def thirdparty(self):
        """Contrasted to busybox, these require external installation.

        As a result it'll be of value to check that they're even in
        the namespace.
        """
        self.user_aliases += [
            ("ag", "ag --hidden --color --no-column %l"),
            ("cat", "bat %l"),
            ("nvim", "nvim %l"),
            ("nman", 'nvim -c "Man %l" -c"wincmd T"'),
            ("tre", "tree -DAshFC --prune -I .git %l"),
        ]


class WindowsAliases(CommonAliases):
    """Aggregated Window aliases. Provides simplified system calls for NT.

    Methods
    -------
    Implements aliases specific to cmd or powershell.

    Notes
    -----
    Would it be useful to subclass :class:`reprlib.Repr` here?

    """

    def __repr__(self):
        return "Windows Aliases: {!r}".format(len(self.user_aliases))

    def cmd_aliases(self):
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
        self.user_aliases += [
            ("assoc", "assoc %l"),
            ("cd", "cd %l"),
            ("chdir", "chdir %l"),
            ("cl", "cl %l"),
            ("cmd", "cmd /U /E:ON /F:ON %l"),
            ("control", "control %l"),
            ("controlpanel", "control %l"),
            ("copy", "copy /V /Y %s %s"),
            # ("cp", "copy %s %s"),
            ("cpanel", "control %l"),
            ("cygpath", "cygpath %l"),
            ("dism", "dism"),
            ("ddir", "dir /ad /on %l"),
            ("echo", "echo %l"),
            ("find", "find %l"),
            ("findstr", "findstr %l"),
            ("finger", "finger"),
            ("ldir", "dir /ad /on %l"),
            ("ll", "dir /Q %l"),
            # I know this really isn't the same but I need it
            ("ln", "mklink %s %s"),
            ("make", "make.bat %l"),  # Useful when we're building docs
            ("mklink", "mklink %s %s"),
            ("move", "move %s %s"),
            ("msbuild", "msbuild %l"),
            ("mv", "move %s %s"),
            ("net", "net %l"),
            ("path", "path %l"),
            ("ren", "ren %l"),
            ("rm", "del %l"),
            ("rmdir", "rmdir %l"),
            # i'll admit this is specific but I'm NEVER gonna remember it
            ("rmdir -r", "rmdir /S %l"),
            ("sc", "sc %l"),
            (
                "set",
                "set %l",
            ),  # but honestly might just work better as os.environ.putenv
            ("sfc", "sfc %l"),
            ("start", "start %l"),
            ("tasklist", "tasklist %l"),
            ("taskkill", "taskkill %l"),
            ("title", "title %l"),
            ("tree", "tree /A /F %l"),
            ("type", "type"),
            ("ver", "ver %l"),
            ("verify", "verify %l"),
            ("vol", "vol %l"),
            ("xcopy", "xcopy %l"),
            ("where", "where %l"),
            ("wmic", "wmic %l"),
        ]

    def powershell_aliases(self):
        r"""Aliases for Windows OSes using :command:`powershell`.

        Has only been tested on Windows 10 in a heavily configured environment.

        Niceties such as Git for Windows, ag-silversearcher, ripgrep,
        ConEmu and others have been added.

        The minimum number of assumptions possible have been made; however, note
        that this section is still under development and frequently changes.

        """
        self.user_aliases += [
            ("ac", "Add-Content %l"),
            ("asnp", "Add-PSSnapin %l"),
            ("cat", "Get-Content %l"),
            # ('cd', 'Set-Location %l'),
            ("clc", "Clear-Content %l"),
            # ('clear', 'Clear-History %l'),
            ("conda env", "Get-Conda-Environment %l"),
            ("copy", "Copy-Item %l"),
            ("cp", "Copy-Item %l"),
            ("del", "Remove-Item %l"),
            ("dir", "Get-ChildItem %l"),
            ("echo", "Write-Output %l"),
            # ('history', 'Get-History %l'),
            ("kill", "Stop-Process"),
            ("l", "Get-ChildItem %l"),
            ("ll", "GetChildItem -Verbose %l"),
            ("ls", "Get-ChildItem %l"),
            ("man", "Get-Help %l"),
            ("md", "mkdir %l"),
            ("move", "Move-Item %l"),
            ("mv", "Move-Item %l"),
            # ('popd', 'Pop-Location %l'),
            ("pro", "nvim $Profile.CurrentUserAllHosts"),
            ("ps", "Get-Process %l"),
            # ('pushd', 'Push-Location %l'),
            # ('pwd', 'Get-Location %l'),
            ("ren", "Rename-Item %l"),
            ("rm", "Remove-Item %l"),
            ("rmdir", "Remove-Item %l"),
            ("rp", "Remove-ItemProperty %l"),
            ("rsn", "Remove-PSSession %l"),
            ("rv", "Remove-Variable %l"),
            ("rvpa", "Resolve-Path %l"),
            ("sajb", "Start-Job %l"),
            ("sal", "Set-Alias %l"),
            ("saps", "Start-Process %l"),
            ("sasv", "Start-Service %l"),
            ("sbp", "Set-PSBreakpoint %l"),
            ("select", "Select-Object %l"),
            ("set", "Set-Variable %l"),
            ("si", "Set-Item %l"),
            ("sl", "Set-Location %l"),
            ("sleep", "Start-Sleep %l"),
            ("sls", "Select-String %l"),
            ("sort", "Sort-Object %l"),
            ("sp", "Set-ItemProperty %l"),
            ("spjb", "Stop-Job %l"),
            ("spps", "Stop-Process %l"),
            ("spsv", "Stop-Service %l"),
            ("start", "Start-Process %l"),
            ("stz", "Set-TimeZone %l"),
            ("sv", "Set-Variable %l"),
            ("tee", "Tee-Object %l"),
            ("tree", "tree /F /A %l",),
            ("type", "Get-Content %l"),
            ("where", "Where-Object %l"),
            ("wjb", "Wait-Job %l"),
            ("write", "Write-Output %l"),
        ]


def generate_aliases(aliases=None):
    """Define aliases in case the user needs to redefine

    Parameters
    ----------
    aliases : `list` of `tuple`
        Aliases to rerun. Can be easily generated from `generate_aliases`

    Returns
    -------
    None

    Raises
    ------
    :exc:`traitlets.config.application.ApplicationError`
        Raises an ApplicationError if `get_ipython` returns an object that
        doesn't have an attribute 'alias_manager'.

    Examples
    --------
    >>> shell = get_ipython()
    >>> len(shell.alias_manager.user_aliases)  # DOCTEST: +SKIP
        0 # and even if it's not
    >>> shell.alias_manager.user_aliases = [('a', 'a'), ('b', 'b'), ('c', 'c')]
    >>> redefine_aliases([('ls', 'ls -F')])
    >>> shell.alias_manager.user_aliases
        4

    """
    _ip = get_ipython()
    if _ip is not None:
        if not hasattr(_ip, "alias_manager"):
            raise ApplicationError
    else:
        return
    machine = platform.platform()

    if machine.startswith("Linux"):
        aliases = LinuxAliases(user_aliases=_ip.alias_manager.user_aliases)
        aliases.busybox()
        aliases.thirdparty()
    elif machine.startswith("Win"):
        aliases = WindowsAliases(user_aliases=_ip.alias_manager.user_aliases)
        aliases.cmd_aliases()
    else:
        raise AliasError
    aliases.ls_patch(_ip)

    return aliases


if __name__ == "__main__":
    all_aliases = generate_aliases()
    # our combined classes have an attribute dict_aliases
    # that makes operations a lot easier to perform
    for i in all_aliases:
        try:
            # so this expression here is how we now we didn't properly separate responsibilities
            all_aliases.soft_define_alias(*i)
        except InvalidAliasError:
            raise

    get_ipython().run_line_magic("alias_magic", "p pycat")
    get_ipython().alias_manager.define_alias("fzf", "fzf-tmux")
