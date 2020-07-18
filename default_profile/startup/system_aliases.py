#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create OS specific aliases to allow a user to use IPython anywhere.

Try to make viewing large amounts of aliases a bit more manageable.

As a product of running `%rehashx` the alias magic is unusable.

Therefore, we try to properly map aliases as dictionaries.

This implies adding enough dunders to the CommonAliases class
constructed here that it appropriately follows the ``mapping`` protocol
as specified in the Python Language Reference.

As stated in the language reference under Common Sequence Operations.:

.. compound::

    Concatenating immutable sequences always results in a new object.
    This means that building up a sequence by repeated concatenation
    will have a quadratic runtime cost in the total sequence length.
    To get a linear runtime cost, you must switch to one of the
    alternatives below:

        - **If concatenating tuple objects, extend a list instead.**

"""
import copy
import gc
import keyword
import operator
import os
import platform
import reprlib
from collections import UserDict
from typing import Any, AnyStr, Optional, Union, Dict

from IPython.core.alias import default_aliases
from IPython.core.getipython import get_ipython

from default_profile.ipython_config import (
    AliasError,
    ApplicationError,
    InvalidAliasError,
    UsageError,
)


def validate_alias(alias) -> Optional[Any]:
    # Remember that you moved that docstring to docs
    if alias.shell is None:
        return
    if not hasattr(alias, "name"):
        raise InvalidAliasError("Alias does not have name attribute.")
    try:
        # Jesus christ this is gonna be something else to untangle
        caller = alias.shell.magics_manager.magics["line"][alias.name]
    except KeyError:
        pass

    nargs = alias.cmd.count("%s") - alias.cmd.count("%%s")
    if (nargs > 0) and (alias.cmd.find("%l") >= 0):
        raise InvalidAliasError(
            "The %s and %l specifiers are mutually " "exclusive in alias definitions."
        )

    return nargs


class Alias(UserDict):
    """Callable object storing the details of one alias.

    Reasonably this is the object that should be the UserDict. CommonAliases
    makes more sense as a list of dicts.

    Instances are registered as magic functions to allow use of aliases.

    Methods
    -------
    blacklist : method
        Previously a class attribute, the blacklist is now a property of an Alias.

    """

    # For as many dunder as this whole module has i barely use any if at all
    # However you gotta debug something related to the reflection of this class
    # `ls??` just raised. The stack trace was in IPython.core.oinspect
    # class Inspector method _get_info. Or possibly that append_field closure.
    # which contains a call to _mime_format so somewhere around there though

    def __init__(
        self, name: AnyStr, cmd: AnyStr, **kwargs: Optional[Dict[AnyStr, AnyStr]]
    ):
        """Validate the alias, and return the number of arguments."""
        super().__init__(**kwargs)
        self.name = name
        self.cmd = cmd
        if self.name in self.blacklist:
            # Wait can we note that we didn't checkout the keyword list though.
            raise InvalidAliasError(
                f"The name {self.name} can't be aliased because it is a keyword or builtin."
            )
        self.nargs = validate_alias(self)

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

    def __eq__(self, other):
        if other.items() == self.items():
            return True


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
        self.linemagics = None
        if user_aliases is None:
            self.user_aliases = default_aliases()
        else:
            self.user_aliases = user_aliases
        if hasattr(user_aliases, "update"):  # did we get a dict?
            self.dict_aliases = self.user_aliases
        elif hasattr(user_aliases, "append"):  # did we get a list of tuples?
            self.dict_aliases = self.tuple_to_dict(self.user_aliases)
        else:
            self.dict_aliases = {}
        self.git()
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
        caller = Alias(name=name, cmd=cmd)
        try:
            self.shell.magics_manager.register_function(
                caller, magic_kind="line", magic_name=name
            )
        except AliasError:
            return

    def is_alias(self, name):
        """Return bool verifying if a name is defined in 'dict_aliases.keys()'."""
        return name in self.dict_aliases.keys()

    def soft_define_alias(self, name, cmd):
        """Define a new alias and don't raise an error on an invalid alias."""
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

    def __repr__(self):
        return "<{}>: {} aliases".format(self.__class__.__name__, len(self.aliases))

    @reprlib.recursive_repr
    def __str__(self):
        return "<{}>\n{}".format(
            self.__class__.__name__, self.repr_dict(self.aliases_dict, self.maxdict)
        )

    def update(self, other, **kwargs):
        """Update the mapping of aliases to system commands.

        Ensure that this is properly defined as this can be critical for speed.

        If a TypeError is raised by doing so then attempt to pass the alias along
        to the shell's `AliasManager` with `soft_define_alias`.

        :param kwargs: Any keyword arguments to pass to the superclass.
        :type kwargs: dict
        :param other: Other object to update instance dict with.

        """
        try:
            self.dict_aliases.update(other)
        except TypeError:
            self.soft_define_alias(*other)
        if kwargs:
            super().update(other=kwargs)

    # def __copy__(self):
    #     return copy.copy(self.dict_aliases)

    def __contains__(self, other):
        if type(other) == Alias:
            for i in self.dict.aliases:
                if other == i:
                    return True
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

    def __index__(self, other):
        # I think the difference is ``__getitem__`` ==> ReprAlias['ls']
        # and ``__index__`` ==> ReprAlias[0].
        return index(self.keys(), other)

    def keys(self):
        # Well of course the above doesn't work i never defined keys
        return self.aliases_dict.keys()

    def __next__(self):
        max = len(self)
        if max >= self.idx:
            # Reset the loop and raise stopiteration
            self.idx = 0
            raise StopIteration
        self.idx += 1
        return self.dict_aliases[self.idx]

    def __getitem__(self, index):
        try:
            return operator.getitem(self.kb.bindings, index)
        except TypeError:
            raise

    def len(self):
        return self.__len__()

    def __getattr__(self, attr):
        try:
            return operator.getattr(self, attr)
        except KeyError:
            raise AttributeError

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

        I want to do a check for if pydoc and apropos are in the aliases.

        .. todo::
            os.environ => env

        """
        if "pydoc" in self.dict_aliases.keys():
            self.unalias("pydoc")
            import pydoc
        if "apropos" in self.dict_aliases.keys():
            self.unalias("apropos")
            # noinspection PyProtectedMember
            from pydoc import apropos
        if "which" in self.dict_aliases.keys():
            self.unalias("which")
            from shutil import which
        if "chown" in self.dict_aliases.keys():
            self.unalias("chown")
            from shutil import chown

    def git(self):
        self.dict_aliases.update(
            self.tuple_to_dict(
                [
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
                    ("gm", "git merge --stat --progress %l"),
                    ("gma", "git merge --abort %l"),
                    ("gmc", "git merge --continue %l"),
                    ("gmm", "git merge --stat --progress master %l"),
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
            )
        )

    def ls_patch(self):
        self.dict_aliases.update(
            self.tuple_to_dict(
                [
                    ("l", "ls -ChF --hide=NTUSER.* --color=always %l"),
                    ("la", "ls -AhFg --color=always %l"),
                    ("ldir", "ls -pFho --hide=NTUSER.*  --color=always %l | grep /$"),
                    ("lf", "ls -Foh --hide=NTUSER.* --color=always | grep ^- %l"),
                    ("ll", "ls -AgFho --color=always --hide=NTUSER.* %l"),
                    ("ls", "ls -Fh --hide=NTUSER.* --color=always %l"),
                    # alternatively -Altcr
                    ("lr", "ls -gFhtr --hide=NTUSER.*  --color=always %l"),
                    # alternatively could do ls -Altc
                    ("lt", "ls -gFht --hide=NTUSER.* --color=always %l"),
                    ("lx", "ls -Fo --hide=NTUSER.* --color=always | grep ^-..x"),
                ]
            )
        )


class LinuxAliases(CommonAliases):
    """Add Linux specific aliases."""

    def __init__(self, dict_aliases=None, *args, **kwargs):
        self.dict_aliases = dict_aliases if dict_aliases is not None else args
        super().__init__(**kwargs)
        self.busybox()
        self.thirdparty()

    def __repr__(self):
        return "Linux Aliases: {!r}".format(len(self.dict_aliases))

    def busybox(self):
        """Commands that are available on any Unix-ish system.

        Returns
        -------
        dict_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        self.dict_aliases.update(
            self.tuple_to_dict(
                [
                    ("cs", "cd %s && ls -F --color=always %s"),
                    ("cp", "cp -v %l"),  # cp mv mkdir and rmdir are all overridden
                    ("df", "df -ah --total"),
                    ("dU", "du -d 1 -h --apparent-size --all | sort -h | tail -n 10"),
                    ("dus", "du -d 1 -ha %l"),
                    ("echo", "echo -e %l"),
                    ("free", "free -mt"),
                    (
                        "gpip",
                        "export PIP_REQUIRE_VIRTUALENV=0;"
                        "python -m pip %l;"
                        "export PIP_REQUIRE_VIRTUALENV=1 > /dev/null",
                    ),
                    (
                        "gpip2",
                        "export PIP_REQUIRE_VIRTUALENV=0;"
                        "python2 -m pip %l;"
                        "export PIP_REQUIRE_VIRTUALENV=1 > /dev/null",
                    ),
                    (
                        "gpip3",
                        "export PIP_REQUIRE_VIRTUALENV=0;"
                        "python3 -m pip %l;"
                        "export PIP_REQUIRE_VIRTUALENV=1 > /dev/null",
                    ),
                    ("head", "head -n 30 %l"),
                    ("mk", "mkdir -pv %l && cd %l"),  # check if this works. only mkdir
                    ("mkdir", "mkdir -pv %l"),
                    ("mv", "mv -v %l"),
                    ("r", "fc last"),
                    ("redo", "fc last"),
                    # Less annoying than -i but more safe
                    # only prompts with more than 3 files or recursed dirs.
                    ("rm", "rm -Iv %l"),
                    ("rmdir", "rmdir -v %l"),
                    (
                        "default_profile",
                        "cd ~/projects/dotfiles/unix/.ipython/default_profile",
                    ),
                    (
                        "startup",
                        "cd ~/projects/dotfiles/unix/.ipython/default_profile/startup",
                    ),
                    ("tail", "tail -n 30 %l"),
                ]
            )
        )

    def thirdparty(self):
        """Contrasted to busybox, these require external installation.

        As a result it'll be of value to check that they're even in
        the namespace.
        """
        self.dict_aliases.update(
            self.tuple_to_dict(
                [
                    ("ag", "ag --hidden --color --no-column %l"),
                    ("cat", "bat %l"),
                    ("nvim", "nvim %l"),
                    ("nman", 'nvim -c "Man %l" -c"wincmd T"'),
                    (
                        "ph",
                        'pygmentize -v -f terminal256 -P "heading=Pygments, the Python highlighter" -l python3 %s',
                    ),
                    ("tre", "tree -DAshFC --prune -I .git %l"),
                ]
            )
        )


class WindowsAliases(CommonAliases):
    """Aggregated Window aliases. Provides simplified system calls for NT.

    Methods
    -------
    Implements aliases specific to cmd or powershell.

    Notes
    -----
    Would it be useful to subclass :class:`reprlib.Repr` here?

    """

    def __init__(self, dict_aliases: Optional[Dict] = None, *args, **kwargs):
        # if you don't give **kwargs to dict_aliases, then by giving *args as
        # it's definition it ends up becoming a list which will immediately
        # screw everything up.
        self.dict_aliases = dict_aliases if dict_aliases is not None else kwargs
        self.cmd_aliases()
        super().__init__(user_aliases=self.dict_aliases)

    def __repr__(self):
        return "Windows Aliases: {!r}".format(len(self.dict_aliases))

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
            that'll affect :data:`_ip.dict_aliases.mv`?

        Also note :envvar:`DIRCMD` for :command:`dir`.

        """
        self.dict_aliases.update(
            self.tuple_to_dict(
                [
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
                    ("del", "del %l"),
                    ("dism", "dism %l"),
                    ("ddir", "dir /ad /on %l"),
                    ("echo", "echo %l"),
                    ("erase", "erase %l"),
                    ("find", "find %l"),
                    ("findstr", "findstr %l"),
                    ("finger", "finger %l"),
                    # Probably the closest reasonable alternative to ls that i've found
                    ("l", "dir /d %l"),
                    # Actual ls isn't aliases since git on windows provides it
                    ("ldir", "dir /ad /on %l"),
                    ("ll", "dir /Q %l"),
                    # I know this really isn't the same but I need it
                    # ("ln", "mklink %s %s"),
                    ("make", "make.bat %l"),  # Useful when we're building docs
                    ("md", "md %l"),
                    ("mk", "mkdir %s & cd %s"),
                    ("mkdir", "mkdir %l"),
                    ("mklink", "mklink %s %s"),
                    ("move", "move %s %s"),
                    ("msbuild", "msbuild %l"),
                    # ("mv", "move %s %s"),
                    ("net", "net %l"),
                    ("path", "path %l"),
                    ("rd", "rd %l"),
                    ("ren", "ren %l"),
                    ("rename", "rename %l"),
                    # should probably stop doing stuff like this with the real
                    # rm still on path
                    # ("rm", "del %l"),
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
                    ("tre", "tree /A /F %l"),
                    ("tree", "tree %l"),
                    ("type", "type %l"),
                    ("ver", "ver %l"),
                    ("verify", "verify %l"),
                    ("vol", "vol %l"),
                    ("xcopy", "xcopy %l"),
                    ("where", "where %l"),
                    ("wmic", "wmic %l"),
                ]
            )
        )

    def powershell_aliases(self):
        r"""Aliases for Windows OSes using :command:`powershell`.

        Has only been tested on Windows 10 in a heavily configured environment.

        Niceties such as Git for Windows, ag-silversearcher, ripgrep,
        ConEmu and others have been added.

        The minimum number of assumptions possible have been made; however, note
        that this section is still under development and frequently changes.

        """
        self.dict_aliases.update(
            [
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
        )


def generate_aliases() -> Union[None, LinuxAliases, WindowsAliases]:
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

    """
    _ip = get_ipython()
    if _ip is not None:
        if not hasattr(_ip, "alias_manager"):
            raise ApplicationError
    else:
        return
    machine = platform.platform()
    # TODO: Fuck we have to change teh user_aliases to dicts too
    if machine.startswith("Linux"):
        # aliases = LinuxAliases(dict_aliases=_ip.alias_manager.user_aliases)
        aliases = LinuxAliases()
        aliases.busybox()
    elif machine.startswith("Win"):
        # aliases = WindowsAliases(dict_aliases=_ip.alias_manager.user_aliases)
        aliases = WindowsAliases()
    else:
        raise AliasError
    # isn't working. yeah fuck this is still raising we need to do something about this.
    aliases.ls_patch()

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
    gc.collect()

# Vim: set et:
