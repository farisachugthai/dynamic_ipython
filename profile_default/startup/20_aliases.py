#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File for all shell aliases.

IPython Aliases
===============

.. module:: aliases
    :synopsis: Create aliases for :mod:`IPython` to ease use as a system shell.

.. rubric:: Changelog - Mar 03, 2019

    Moved git aliases into new :func:`common_aliases()`


Overview
--------
This module utilizes ``_ip``, the global IPython InteractiveShell
instance, and fills the ``user_ns`` with common Linux idioms.


Parameters
----------
When writing aliases, an ``%alias`` definition can take various string
placeholders. As per the official documentation:


    .. topic:: %l parameter

        You can use the %l specifier in an alias definition to represent the
        whole line when the alias is called.

Meaning that it behaves similarly to the parameter `$*` in shells like eshell.

The documentation goes on to say:

.. ipython::

    In [2]: %alias bracket echo "Input in brackets: <%l>"
    In [3]: bracket hello world
    Input in brackets: <hello world>

Note that we quote when in the configuration file but when running alias
interactively the syntax ``%alias alias_name cmd`` doesn't require quoting.


Attributes
----------
_ip : |ip|
    A global object representing the active IPython session.
    Contains varying packages as well as the current global namespace.
    Doesn't need to be defined in advance during an interactive session.


Examples
--------
This code creates a handful of platform-specific functions where each returns
`user_aliases`. Realizing that this is also used in the :mod:`IPython`
implementation, the source code of the implementation has been provided for reference.

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
--------
Aliases file for IPython.

:mod:`IPython.core.alias`

"""
import logging
import platform
from shutil import which

# from prompt_toolkit import print_formatted_text as print
import IPython
from IPython import get_ipython
from IPython.core.alias import AliasError

logger = logging.getLogger(__name__)


def _sys_check():
    """Check OS."""
    return platform.uname().system


def linux_specific_aliases(_ip):
    r"""Add Linux specific aliases.

    Aliases that have either:

        * Only been tested on Linux
        * Only natively exist on Linux
        * Clobber an existing Windows command (cmd in particular)

    Convenience packages exist such as ConEmu or Cmder which allow a large
    number of GNU/Linux built-ins to exist on Windows, and as a result, this
    list may not be comprehensive.

    Yet to be implemented
    ---------------------
    - ``ssh-day``
    - ``extract``
    - :command:`fzf` in its many invocations.

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
        ('ag', 'ag --hidden --color %l'),
        ('cs', 'cd %s && ls -F --color=always %s'),
        ('cp', 'cp -iv %l'),  # cp mv mkdir and rmdir are all overridden
        ('dus', 'du -d 1 -h %l'),
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
        ('nman', 'nvim -c "Man $1" -c"wincmd T"'),
        ('r', 'fc -s'),
        ('redo', 'fc -s'),
        ('rm', 'rm -v %l'),
        ('rmdir', 'rmdir -v %l'),
        ('profile_default',
         'cd ~/projects/dotfiles/unix/.ipython/profile_default/startup'),
        ('startup',
         'cd ~/projects/dotfiles/unix/.ipython/profile_default/startup'),
        ('tail', 'tail -n 30 %l'),
        ('tre', 'tree -ashFC -I .git -I __pycache__ --filelimit 25'),
    ]
    return _user_aliases


def common_aliases(_ip=None):
    r"""Add aliases common to all OSes.

    Parameters
    ----------
    _ip : |ip|
        The global instance of IPython.


    Returns
    -------
    _ip.user_aliases : list
        User aliases.

    """
    _user_aliases = [
        ('g', 'git diff --staged --stat'),
        ('ga', 'git add %l'),
        ('ga.', 'git add .'),
        ('gar', 'git add --renormalize %l'),
        ('gb', 'git branch -a %l'),
        ('gci', 'git commit %l'),
        ('gcia', 'git commit --amend %l'),
        ('gcid', 'git commit --date=%l'),
        ('gciad', 'git commit --amend --date=%l'),
        ('gcl', 'git clone %l'),
        ('gcls', 'git clone --depth 1 %l'),
        ('gco', 'git checkout %l'),
        ('gcob', 'git checkout -b %l'),
        ('gd', 'git diff %l'),
        ('gds', 'git diff --staged %l'),
        ('gds2', 'git diff --staged --stat %l'),
        ('gdt', 'git difftool %l'),
        ('gf', 'git fetch --all'),
        ('git', 'git %l'),
        ('git hist',
         'git log --pretty="format:%h %ad | %d [%an]" --graph --date=short --branches --abbrev-commit --oneline '
         ),
        ('git last', 'git log -1 HEAD %l'),
        ('git staged', 'git diff --cached %l'),
        ('git rel', 'git rev-parse --show-prefix'),
        ('git root', 'git rev-parse --show-toplevel'),
        ('git unstage', 'git reset HEAD'),
        ('git unstaged', 'git diff %l'),
        ('gl', 'git log %l'),
        ('glo', 'git log --graph --decorate --abbrev-commit --oneline --branches --all'),
        ('gls', 'git ls-tree'),
        ('gm', 'git merge --no-ff %l'),
        ('gmm', 'git merge master'),
        ('gmt', 'git mergetool %l'),
        ('gp', 'git pull --all'),
        ('gpo', 'git pull origin'),
        ('gpom', 'git pull origin master'),
        ('gpu', 'git push'),
        ('gr', 'git remote -v'),
        ('gs', 'git status'),
        ('gsh', 'git stash'),
        ('gshp', 'git stash pop'),
        ('gshl', 'git stash list'),
        ('gshd', 'git stash drop'),
        ('gshc', 'git stash clear'),
        ('gsha', 'git stash apply'),
        ('gst', 'git diff --stat %l'),
        ('gt', 'git tag --list'),
        ('lswitch', 'legit switch'),
        ('lsync', 'legit sync'),
        ('lpublish', 'legit publish'),
        ('lunpublish', 'legit unpublish'),
        ('lundo', 'legit undo'),
        ('lbranches', 'legit branches'),
        ('xx', 'quit'),  # this is a sweet one
        ('..', 'cd ..'),
        ('...', 'cd ../..'),
    ]
    return _user_aliases


def windows_aliases(_ip=None):
    """How did these get deleted!"""
    _ip.user_aliases = [
        ('copy', 'copy'),
        ('ddir', 'dir /ad /on'),
        ('echo', 'echo'),
        ('ldir', 'dir /ad /on'),
        ('ls', 'dir /on'),
        ('mkdir', 'mkdir'),
        ('mklink', 'mklink'),
        ('ren', 'ren'),
        ('rmdir', 'rmdir'),
        (
            'tree',
            'tree /F /A %l',
        ),
    ]
    return _ip.user_aliases


if __name__ == "__main__":
    _ip = get_ipython()

    if not isinstance(_ip, IPython.terminal.interactiveshell.InteractiveShell):
        raise Exception

    # Pretty sure we could swap these calls out for `_ip.logger.logwrite`'s
    logging.basicConfig(level=logging.WARNING)

    user_aliases = []

    if _sys_check() == 'Linux':

        # Now let's get the Linux aliases.
        user_aliases += linux_specific_aliases(_ip)
        logging.info("The number of available aliases is: " +
                     str(len(user_aliases)))

        if platform.machine() == "aarch64":
            # user_aliases += termux_aliases(ip)
            pass

    user_aliases += common_aliases(_ip)

    # There has got to be a better way to do this.
    if which('fzf') and which('rg'):
        user_aliases.extend(
            ('fzf', '$FZF_DEFAULT_COMMAND | fzf-tmux $FZF_DEFAULT_OPTS'))
    elif which('fzf') and which('ag'):
        pass  # TODO

    logging.info("The number of available aliases is: " +
                 str(len(user_aliases)))

    for i in user_aliases:
        try:
            _ip.alias_manager.define_alias(i[0], i[1])
        except AliasError as e:
            logging.error(e)

    del i, _sys_check
