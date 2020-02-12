#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create OS specific aliases to allow a user to use IPython anywhere."""
from collections import UserDict
import logging
import os
import shutil
import subprocess
import traceback

# from IPython.core.alias import AliasManager, default_aliases, AliasError
from IPython.core.alias import InvalidAliasError, default_aliases
from IPython.core.getipython import get_ipython
from traitlets.config.application import ApplicationError


class CommonAliases(UserDict):
    r"""Add aliases common to all OSes. Overwhelmingly :command:`Git` aliases.

    This method adds around 100 aliases that can be
    implemented on most of the major platforms.

    The only real requirement is Git being installed and working. Docker
    commands possibly going to be added.

    .. todo:: :command:`git show`

    .. todo:: The class method doesn't work if we don't have a class attribute.

        But if we create a class attribute, does updating the aliases for an instance
        change it for subclasses? Write a test to ensure that this isn't what
        happens.

    """

    def __init__(self, shell=None, user_aliases=None, **kwargs):
        """OS Agnostic aliases.

        Parameters
        ----------
        user_aliases : list of ('alias', 'system command') tuples
            User aliases to add the user's namespace.

        """
        self.shell = shell or get_ipython()

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

    def alias_manager(self):
        return self.shell.alias_manager

    def define_alias(self, name, cmd):
        self.alias_manager.define_alias(name, cmd)

    def soft_define_alias(self, name, cmd):
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

    def __iter__(self):
        return self._generator()

    def _generator(self):
        for itm in self.dict_aliases:
            yield itm

    def __repr__(self):  # reprlib?
        return "<Common Aliases>: # of aliases: {!r} ".format(len(self.dict_aliases))

    # def __contains__(self, other):
    # is this the right definition for contains?
    # if other in self.dict_aliases:
    # return True
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

        Note
        ----
        shutil.which actually checks :envvar:`PATHEXT`! That's real nice.

        """
        return shutil.which(exe)

    def extend(self, list_aliases):
        """Implement the method `extend` in a similar way to how `list.extend` works.

        Parameters
        ----------
        list_aliases : list of tuple
        """
        for i in list_aliases:
            self.shell.alias_manager.define_alias(*alias)

    def update(self, other):
        """Properly map aliases as dictionaries.

        As stated in the language reference under Common Sequence Operations.:

            Concatenating immutable sequences always results in a new object.
            This means that building up a sequence by repeated concatenation
            will have a quadratic runtime cost in the total sequence length.
            To get a linear runtime cost, you must switch to one of the
            alternatives below:

                - **If concatenating tuple objects, extend a list instead.**

        """
        try:
            self.dict_aliases.update(other)
        except TypeError:
            raise

    def __add__(self, name=None, cmd=None, *args):
        """Allow name or cmd to not be specified. But if you pass non-kwargs please keep it in a tuple."""
        # I think i made this as flexible as possible. Cross your fingers.
        if name is None and cmd is None:
            if len(args) != 2:
                raise AliasError
            else:
                name, cmd = args
        self.define_alias(name, cmd)

    def __mul__(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.dict_aliases)

    def len(self):
        return self.__len__()

    def append(self, list_aliases):
        for i in list_aliases:
            self.shell.alias_manager.define_alias(alias)

    def __getattr__(self, attr):
        """Define a getattr as dicts typically don't have one defined."""
        return getattr(self, attr)
    
    def tuple_to_dict(self, list_of_tuples):
        """Showcasing how to convert a tuple into a dict.

        Nothing particularly hard, just a good exercise.
        Also some good docstring practice!

        Parameters
        ----------
        color_templates : tuple of tuples
        Each element maps ANSI escape codes to the colors they represent.

        Returns
        -------
        Flattened dict : dict with {str: str} for each element
            Maps exactly as intended and reduces a little of the nesting.

        Examples
        --------
        ::

            In [3]: tuple_to_dict(color_templates)
            Out[14]:
            {'Black': '0;30',
            'Red': '0;31',
            'Green': '0;32',
            'Brown': '0;33',
            'Blue': '0;34',
            'Purple': '0;35',
            'Cyan': '0;36',
            'LightGray': '0;37',
            'DarkGray': '1;30',
            'LightRed': '1;31',
            'LightGreen': '1;32',
            'Yellow': '1;33',
            'LightBlue': '1;34',
            'LightPurple': '1;35',
            'LightCyan': '1;36',
            'White': '1;37',
            'BlinkBlack': '5;30',
            'BlinkRed': '5;31',
            'BlinkGreen': '5;32',
            'BlinkYellow': '5;33',
            'BlinkBlue': '5;34',
            'BlinkPurple': '5;35',
            'BlinkCyan': '5;36',
            'BlinkLightGray': '5;37'}

        """
        a = list_of_tuples
        if a is None:
            a = self.user_aliases
        ret = {}
        for i, j in enumerate(a):
            ret[a[i][0]] = a[i][1]

        return ret

    def unalias(self, alias):
        """Remove an alias.

        .. magic:: unalias

        Parameters
        ----------
        alias : Alias to remove

        """
        self.shell.run_line_magic("unalias", alias)

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
        """100+ git aliases.

        Notes
        -----
        Aliases of note.

        - gcls: git clone [url]

            - This uses the ``%s`` argument to indicate it requires 1 and only 1 argument as git clone does

            - Note this is in contrast to gcl, or git clone, as that can have additional options specified

        - gcim: git commit --message [message]

            - Also uses ``%s``

        Unless otherwise noted every alias uses ``%l`` to allow the user to specify
        any relevant options or flags on the command line as necessary.

        Returns
        -------
        user_aliases : A list of tuples
            The format of IPython aliases got taken it's logical conclusion
            and probably pushed a little further than that.

            In order to make new subcommands in a way similar to how git allows
            one to come up with aliases, I first tried using whitespace in
            the alias.::

                ('git last', 'git log -1 HEAD %l')

            However that simply registers the word ``git`` as an alias and then
            sends ``git last`` to the underlying shell, which it may or may
            not recognize.

            Therefore I tried using a hyphen to separate the words, but the
            python interpreter uses hyphens as well as whitespace to separate
            keywords, and as a result, would split the alias in the middle of
            the command.

        Examples
        --------
        ::

            In [58]: %git_staged?
            Object `staged` not found.

            In [60]: %git_staged?
            Object `%git_staged` not found.

        """
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
            ("gm", "git merge --no-ff %l"),
            ("gma", "git merge --abort %l"),
            ("gmc", "git merge --continue %l"),
            ("gmm", "git merge --no-ff master %l"),
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
        return self.user_aliases

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
        return self.user_aliases


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
        self.user_aliases = [
            ("assoc", "assoc %l"),
            ("cd", "cd %l"),
            ("chdir", "chdir %l"),
            ("cmd", "cmd /U /E:ON /F:ON %l"),
            ("control", "control %l"),
            ("controlpanel", "control %l"),
            ("copy", "copy %s %s"),
            ("cp", "copy %s %s"),
            ("cpanel", "control %l"),
            ("ddir", "dir /ad /on %l"),
            ("echo", "echo %l"),
            ("ldir", "dir /ad /on %l"),
            ("ll", "dir /Q %l"),
            # I know this really isn't the same but I need it
            ("ln", "mklink %s %s"),
            ("make", "make.bat %l"),  # Useful when we're building docs
            ("mklink", "mklink %s %s"),
            ("move", "move %s %s"),
            ("mv", "move %s %s"),
            ("path", "path %l"),
            ("ren", "ren %l"),
            ("rm", "del %l"),
            ("rmdir", "rmdir %l"),
            # i'll admit this is specific but I'm NEVER gonna remember it
            ("rmdir -r", "rmdir /S %l"),
            ("sfc", "sfc %l"),
            ("tasklist", "tasklist %l"),
            ("taskkill", "taskkill %l"),
            ("tree", "tree /A /F %l"),
            ("where", "where %l"),
        ]
        return cls.user_aliases

    def powershell_aliases(self):
        r"""Aliases for Windows OSes using :command:`powershell`.

        Has only been tested on Windows 10 in a heavily configured environment.

        Niceties such as Git for Windows, ag-silversearcher, ripgrep,
        ConEmu and others have been added.

        The minimum number of assumptions possible have been made; however, note
        that this section is still under development and frequently changes.

        """
        self.user_aliases = [
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
        return cls.user_aliases

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


def generate_aliases(_ip=None):
    """Set up aliases for the user namespace for IPython.

    Planning on coming up with a new way of introducing the aliases into the user namespace.

    # TODO: Work in the Executable() class check.
    """
    if _ip is None:
        _ip = get_ipython()
    if not hasattr(_ip, "magics_manager"):
        raise ApplicationError("Are you running in IPython?")

    common_aliases = CommonAliases(
        shell=_ip, user_aliases=_ip.alias_manager.user_aliases
    )
    from default_profile.util.machine import Platform

    machine = Platform()

    if machine.is_linux:
        linux_aliases = LinuxAliases()
        # common_aliases.user_aliases.append(linux_aliases.user_aliases)
    elif machine.is_windows:
        windows_aliases = WindowsAliases()
        # common_aliases.user_aliases.append(windows_aliases.user_aliases)

    # TODO: allow adding of these classes
    return common_aliases


def redefine_aliases(aliases, shell=None):
    """Now a function to allow the user to rerun as necesaary.

    Parameters
    ----------
    aliases : list of tuples
        Aliases to rerun. Can be easily generated from `generate_aliases`

    Returns
    -------
    None

    Raises
    ------
    :exc:`traitlets.config.application.ApplicationError`

    Examples
    --------
    >>> shell = get_ipython()
    >>> len(shell.alias_manager.user_aliases)  # DOCTEST: +SKIP
        3
    >>> # and even if it's not
    >>> shell.alias_manager.user_aliases = [('a', 'a'), ('b', 'b'), ('c', 'c')]
    >>> redefine_aliases([('ls', 'ls -F')])
    >>> shell.alias_manager.user_aliases
        4

    """
    if shell is None:
        shell = get_ipython()
    if not hasattr(shell, "alias_manager"):
        raise ApplicationError
    for i, j in enumerate(aliases):
        try:
            shell.alias_manager.define_alias(j, all_aliases.dict_aliases[j])
        except InvalidAliasError:
            raise


if __name__ == "__main__":
    _ip = get_ipython()

    if _ip is not None:
        all_aliases = generate_aliases()
        # our combined classes have an attribute dict_aliases
        # that makes operations a lot easier to perform
        redefine_aliases(all_aliases.dict_aliases)
        from default_profile.util.module_log import stream_logger

        ALIAS_LOGGER = stream_logger(
            logger="default_profile.startup.20_aliases",
            msg_format=(
                "[ %(name)s  %(relativeCreated)d ] %(levelname)s %(module)s %(message)s "
            ),
            log_level=logging.WARNING,
        )

        ALIAS_LOGGER.info("Number of aliases is: %s" % all_aliases)
        _ip.run_line_magic("alias_magic", "p pycat")
