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
import atexit
import logging
import os
from pathlib import Path
import platform
import sys
import traceback

from IPython.core.getipython import get_ipython

if os.environ.get("IPYTHONDIR"):
    LOG_FILENAME = os.path.join(os.environ.get("IPYTHONDIR"), "completer.log")
    logging.basicConfig(
        format="%(message)s", filename=LOG_FILENAME, level=logging.DEBUG,
    )
else:
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)


class SimpleCompleter:
    """Completion mechanism that tracks candidates for different subcommands.

    :URL: https://pymotw.com/3/readline/

    The SimpleCompleter class keeps a list of options that are candidates
    for auto-completion. The *complete* method for an instance is designed
    to be registered with `readline` as the source of completions.

    """

    def __init__(self, options):
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
        response = None
        if state == 0:
            # This is the first time for this text,
            # so build a match list.
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
                logging.debug("%s matches: %s", repr(text), self.matches)
            else:
                self.matches = self.options[:]
                logging.debug("(empty input) matches: %s", self.matches)

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug("complete(%s, %s) => %s", repr(text), state, repr(response))
        return response


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


def readline_config():
    """The main point of execution for the readline configs.

    Should be cross-platform and independent of GNU readline or py readline.

    This sets up history where the history file is saved to and calls
    `atexit` with the `setup_historyfile` and `teardown_historyfile` functions
    as parameters.

    """
    # Dude how refreshing is that
    readline.parse_and_bind('"Up": history-search-forward')
    readline.parse_and_bind('"Down": history-search-backward')
    # readline.parse_and_bind('"\\C-d": end-of-file')

    readline.parse_and_bind('"\\C-a": beginning-of-line')
    readline.parse_and_bind('"\\C-b": backward-char')
    readline.parse_and_bind('"\\C-e": end-of-line')
    readline.parse_and_bind('"\\C-f": forward-char')
    readline.parse_and_bind('"\\C-g": abort')
    readline.parse_and_bind('"\\C-h": backward-delete-char')
    readline.parse_and_bind('"\\C-i": complete')
    readline.parse_and_bind('"\\C-j": accept-line')
    readline.parse_and_bind('"\\C-k": "kill-whole-line"')
    readline.parse_and_bind('"\\C-l": clear-screen')
    readline.parse_and_bind('"\\C-m": accept-line')
    # readline.parse_and_bind('"\\C-n": menu-complete')
    # readline.parse_and_bind('"\\C-p": menu-complete-backward')
    # "\C-q": quoted-insert
    readline.parse_and_bind('"\\C-r": reverse-search-history')
    readline.parse_and_bind('"\\C-s": forward-search-history')
    # readline.parse_and_bind('"\\C-t": transpose-chars')
    readline.parse_and_bind('"\\C-u": unix-line-discard')
    # "\C-v": quoted-insert
    # readline.parse_and_bind('"\\C-w": unix-filename-rubout')
    readline.parse_and_bind('"\\C-y": yank')
    # readline.parse_and_bind('"\\C-x\\C-g": abort')
    # readline.parse_and_bind('"\\C-x\\C-r": re-read-init-file')

    # Whew!
    readline.parse_and_bind('"\\C-]": character-search')
    readline.parse_and_bind('"\\C-_": undo')
    # readline.parse_and_bind('\\e\C-]": character-search-backward')
    readline.parse_and_bind('"Insert": overwrite-mode')
    # readline.parse_and_bind("Meta-/: complete")
    # readline.parse_and_bind('"\\eb": backward-word')
    # readline.parse_and_bind('"\\ef": forward-word')
    # readline.parse_and_bind('"\\e?": possible-completions')
    # readline.parse_and_bind('"\\e/": possible-completions')
    # readline.parse_and_bind('"\\ed": kill-word')
    # readline.parse_and_bind('"Meta-Tab": tab-insert')
    # "\er": redraw-current-line
    # readline.set_completer(Completer().complete


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


def setup_historyfile(filename=None):
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
            logging.exception("Could not create the history file.")

    histfile_str = str(histfile)
    try:
        readline.read_history_file(histfile_str)
    except OSError as e:
        logging.exception("Could not read the history file.")
    else:
        readline.set_history_length(2000)

    # now ipython
    shell = get_ipython()
    if shell is None:
        return
    shell.events.register("post_run_cell", add_last_input)


def teardown_historyfile(starting_id, histfile=None):
    if not hasattr(readline, "append_history_file"):
        return
    new_h_len = readline.get_current_history_length()
    readline.set_history_length(2000)
    try:
        readline.append_history_file(new_h_len - starting_id, histfile)
    except OSError:
        logging.error(
            "History not saved. There were problems saving to ~/.python_history"
        )


def last_input():
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
        try:
            import readline
        except ImportError:
            readline = None
        else:
            # Only immport rlcompleter if we're on linux. pyreadline
            # doesn't match all of it's API
            import rlcompleter
            from rlcompleter import Completer

    else:
        # All the pyreadline submodules have to be called as pyreadline.
        # not all clases show up though, so they have to be called as readline
        # in that case
        from pyreadline.lineeditor.lineobj import ReadLineTextBuffer
        from readline import GetOutputFile  # output console via ctype
        # oh also call the pyreadline top module
        import readline

        out_console = GetOutputFile()
        from pyreadline.console.ansi import AnsiState, AnsiWriter

        # from pyreadline import append_history_file
        rl_class = Readline()
        pyreadline_specific(rl_class)
        # not needed yet but a good reminder of the API
        # from pyreadline.modes.emacs import EmacsMode
        # from pyreadline.modes.vi import ViMode, ViExternalEditor, ViCommand

        # emacs_mode = EmacsMode(pyreadline.Readline())
        # vi_mode = ViMode(pyreadline.Readline())

    if readline is not None:
        history_file = os.path.expanduser("~/.python_history")
        setup_historyfile(history_file)
        original_hist_length = readline.get_current_history_length()
        readline.read_history_file(history_file)
        atexit.register(readline.write_history_file, history_file)
        atexit.register(
            teardown_historyfile, original_hist_length, histfile=history_file
        )
        # readline.set_startup_hook(readline_config())
