#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module where readline is properly configured before prompt_toolkit is loaded.

Summary
-------
In tandem with :file:`../pyreadlineconfig.ini`, keybindings
are set up to attempt adding the standard readline bindings
to Vim insert mode.

Extended Summary
----------------
The keybindings that prompt_toolkit provides are more powerful;
however they're substantially more complicated and for simple
modifications of how to work with a line-editor buffer, this proves
needlessly complex in addition to periodically leaving the entire
terminal in an unusuable state.

See Also
--------
`Tim Pope's RSI Vim plugin <https://github.com/tpope/vim-rsi>`_.

"""
import asyncio
import atexit
import codecs
import logging
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import tempfile
import traceback
from typing import Union, Any, AnyStr, Iterable, Optional

from IPython.core.getipython import get_ipython

try:
    import readline
except ImportError:
    readline = None

from default_profile.site_customize import write_history

if os.environ.get("IPYTHONDIR"):
    LOG_FILENAME: Union[AnyStr, os.PathLike]
    LOG_FILENAME = os.path.join(os.environ.get("IPYTHONDIR"), "completer.log")
    logging.basicConfig(
        format="%(message)s", filename=LOG_FILENAME, level=logging.DEBUG,
    )
else:
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)


logger = logging.getLogger(name=__name__)


# Patching pyreadline:


class ViExternalEditor:
    """If I'm not mistaken, there are typos that are causing Vi mode to fail.

    03/22/2020:
    After pressing :kbd:`Esc` to go into Normal mode, I tried invoking the
    external editor with :kbd:`k`.

    .. code-block:: py3tb

        >>> def cd(arg):
        >>>     pass

    Let's see what happens if we get rid of the space between file and ``(``

    Alright well in my defense this class was created quitely poorly; however,
    it's a little too easy to initialize this sucker with no state.
    """

    def __init__(self, line: AnyStr=None):
        """Instantiate the editor :command:`vi`.

        Parameters
        ----------
        line : str
            Line that the user is typing.

        """
        if line is not None:
            if isinstance(line, list):
                line = "".join(i for i in line)
            elif isinstance(line, bytes):
                line = codecs.decode(line, 'utf-8')
        else:
            line = ""

    def __repr__(self):
        return f"{self.__class__.__name__}>:"

    def __call__(self, filename: Optional[Union[AnyStr, os.PathLike]]=None):
        return self.run_editor(filename)

    def run_editor(self, filename: Optional[Union[AnyStr, os.PathLike]]=None):
        """It's the goddamn ViExternalEditor default to Vim!"""
        try:
            editor = os.environ["EDITOR"]
        except KeyError:
            editor = "vim"

        if filename is None:
            filename = tempfile.mktemp(prefix="readline-", suffix=".py")

        with open(filename, "rt+") as fp_tmp:
            fp_tmp.write(line)
            cmd = [editor, filename]
            return self.run_command(cmd)

    def run_command(self, command: AnyStr):
        return subprocess.run(
            shlex.split(shlex.quote(command)),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

    async def async_run_command(self, command: AnyStr):
        # Did i do this right?
        proc = await asyncio.subprocess.run(
            shlex.split(shlex.quote(command)),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )


# Completion


class SimpleCompleter:
    """Completion mechanism that tracks candidates for different subcommands.

    :URL: https://pymotw.com/3/readline/

    The SimpleCompleter class keeps a list of options that are candidates
    for auto-completion. The *complete* method for an instance is designed
    to be registered with `readline` as the source of completions.

    """

    def __init__(self, options: Iterable):
        self.options = sorted(options)

    def complete(self, text, state):
        """Complete a user's input.

        The arguments are a text string to complete and a state value,
        indicating how many times the function has been called with the
        same text.

        The function is called repeatedly with the state incremented
        each time. It should return a string if there is a candidate for that
        state value or None if there are no more candidates.

        The implementation of *complete* here looks for a set of
        matches when state is 0, and then returns all of the candidate matches
        one at a time on subsequent calls.
        """
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
                logger.debug("%s matches: %s", repr(text), self.matches)
            else:
                self.matches = self.options[:]
                logger.debug("(empty input) matches: %s", self.matches)

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logger.debug("complete(%s, %s) => %s", repr(text), state, repr(response))
        return response


def complete(text, state):
    """If no text in front of the cursor, return 4 spaces. Otherwise use the standard completer."""
    if not text:
        # Insert four spaces for indentation
        return ("    ", None)[state]
    else:
        if readline is not None:
            old_complete = readline.get_completer()
            return old_complete(text, state)


def input_loop():
    r"""Simulate a runnnig loop with a call to `input`.

    .. todo::

        Register the completer function.::

            OPTIONS = ['start', 'stop', 'list', 'print']
            readline.set_completer(SimpleCompleter(OPTIONS).complete)

        Check what the API is to add a completer to ipython.
        I think it's |ip|\`.set_custom_completer`.

    """
    line = ""
    while line != "stop":
        line = input('Prompt ("stop" to quit): ')
        print("Dispatch {}".format(line))


# Readline Config

def gnu_readline_config():
    """Readline configuration that's incompatible with GNU readline.

    Pyreadline doesn't recognize a lot of the standard Readline functions,
    so to avoid emitting warnings upon startup, a handful of bindings
    were separated from `readline_config`.
    """
    readline.parse_and_bind('"Up": history-search-forward')
    readline.parse_and_bind('"Down": history-search-backward')
    readline.parse_and_bind('"\\C-d": end-of-file')
    readline.parse_and_bind('"\\C-g": abort')
    readline.parse_and_bind('"\\C-n": menu-complete')
    readline.parse_and_bind('"\\C-p": menu-complete-backward')
    # "\C-q": quoted-insert
    readline.parse_and_bind('"\\C-r": reverse-search-history')
    readline.parse_and_bind('"\\C-s": forward-search-history')
    readline.parse_and_bind('"\\C-t": transpose-chars')
    readline.parse_and_bind('"\\C-u": unix-line-discard')
    readline.parse_and_bind('"\\C-v": quoted-insert')
    readline.parse_and_bind('"\\C-w": unix-filename-rubout')
    readline.parse_and_bind('"\\C-y": yank')
    readline.parse_and_bind('"\\C-x\\C-g": abort')
    readline.parse_and_bind('"\\C-x\\C-r": re-read-init-file')

    # Whew!
    readline.parse_and_bind('"\\C-]": character-search')
    readline.parse_and_bind('"\\C-_": undo')
    readline.parse_and_bind('"Insert": overwrite-mode')
    readline.set_completer(Completer().complete)


def readline_config():
    """The main point of execution for the readline configs.

    Should be cross-platform and independent of GNU readline or py readline.

    This sets up history where the history file is saved to and calls
    `atexit` with the `setup_historyfile` and `teardown_historyfile` functions
    as parameters.

    """
    readline.parse_and_bind('"\\C-a": beginning-of-line')
    readline.parse_and_bind('"\\C-b": backward-char')
    readline.parse_and_bind('"\\C-e": end-of-line')
    readline.parse_and_bind('"\\C-f": forward-char')
    readline.parse_and_bind('"\\C-h": backward-delete-char')
    readline.parse_and_bind('"\\C-i": complete')
    readline.parse_and_bind('"\\C-j": accept-line')
    readline.parse_and_bind('"\\C-k": "kill-whole-line"')
    readline.parse_and_bind('"\\C-l": clear-screen')
    readline.parse_and_bind('"\\C-m": accept-line')
    # readline.parse_and_bind("Meta-/: complete")
    # readline.parse_and_bind('\\e\C-]": character-search-backward')
    # readline.parse_and_bind('"\\eb": backward-word')
    # readline.parse_and_bind('"\\ef": forward-word')
    # readline.parse_and_bind('"\\e?": possible-completions')
    # readline.parse_and_bind('"\\e/": possible-completions')
    # readline.parse_and_bind('"\\ed": kill-word')
    # readline.parse_and_bind('"Meta-Tab": tab-insert')
    # "\er": redraw-current-line


def pyreadline_specific(rl=None):
    """Utilize the pyreadline API.

    Parameters
    ----------
    :class:`pyreadline.rlmain.Readline`

    Returns
    -------
    Currently None. Seemingly works by modifying attributes on the instance
    and relying on side effects.


    """
    if rl is None:
        return
    # This is actually really neat
    rl.allow_ctrl_c = True
    rl.command_color = "#7daea3"
    # todo: check which mode we're in
    # if pyreadline.editingmodes.
    # readline.read_and_parse('z-=', "redraw-screen")


# History


def setup_historyfile(filename: Optional[Union[AnyStr, os.PathLike]]=None):
    """Add a history file to readline.

    Parameters
    ----------
    filename : str, path, or `os.Pathlike`
        path to the history file. Internally converted to a `pathlib.Path`.

    """
    if filename is None:
        filename = "~/.python_history"
    histfile = Path(filename).expanduser()
    if not histfile.exists():
        try:
            histfile.touch()
        except PermissionError:
            raise
        except OSError:
            logger.exception("Could not create the history file.")

    histfile_str = str(histfile)
    # now ipython
    shell = get_ipython()
    if shell is None:
        return
    shell.events.register("post_run_cell", add_last_input)


def last_input() -> AnyStr:
    """Returns the user's last input.

    Utilizes the *raw_cell* attribute found on an
    :class:`IPython.core.interactiveshell.ExecutionInfo` instance.
    """
    return get_ipython().last_execution_result.info.raw_cell


def add_last_input():
    """Calls readline's `add_history` function with `last_input`."""
    return readline.add_history(last_input())


if __name__ == "__main__":
    # Interestingly this can work on Windows with a simple pip install pyreadline
    # however it can be imported as readline no alias so check it first
    if "pyreadline" in sys.modules:
        pyreadline = sys.modules["pyreadline"]

    try:
        from pyreadline.rlmain import Readline

        # from pyreadline.lineobj.history import EscapeHistory, LineEditor
    except (ImportError, ModuleNotFoundError):
        # Only immport rlcompleter if we're on linux. pyreadline
        # doesn't match all of it's API
        import rlcompleter
        from rlcompleter import Completer
        gnu_readline_config()

    else:
        # All the pyreadline submodules have to be called as pyreadline.
        # not all clases show up though, so they have to be called as readline
        # in that case
        from readline import GetOutputFile  # output console via ctype
        # oh also call the pyreadline top module
        import readline
        # from pyreadline.lineeditor.lineobj import ReadLineTextBuffer
        # from pyreadline.console.ansi import AnsiState, AnsiWriter
        from pyreadline.console import Console
        # from pyreadline.modes.emacs import EmacsMode
        # emacs_mode = EmacsMode(pyreadline.Readline())
        from pyreadline.modes.vi import ViMode, ViCommand
        # from pyreadline import append_history_file

        out_console = GetOutputFile()
        console = Console()
        rl_class = Readline()
        pyreadline_specific(rl_class)
        vi_mode = ViMode(pyreadline.rlmain.Readline())
        vi_mode.complete_filesystem = True

    if readline is not None:
        history_file = os.path.expanduser("~/.python_history")
        # setup_historyfile(history_file)
        # atexit.register(write_history, history_file)
        readline.set_completer_delims("@#$_&-+()/*\"':;!?~`|÷×{}=[]%<>\r\t\n")
        readline_config()
