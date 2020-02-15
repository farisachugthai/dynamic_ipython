#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module where readline is properly configured before prompt_toolkit is loaded."""
import atexit
import logging
import os
from pathlib import Path
import platform
import rlcompleter
from rlcompleter import Completer
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
    """
    :URL: https://pymotw.com/3/readline/

    The SimpleCompleter class keeps a list of options that are candidates
    for auto-completion. The complete() method for an instance is designed
    to be registered with readline as the source of completions.

    The arguments are a text string to complete and a state value,
    indicating how many times the function has been called with the
    same text.

    The function is called repeatedly with the state incremented
    each time. It should return a string if there is a candidate for that
    state value or None if there are no more candidates.

    The implementation of complete() here looks for a set of
    matches when state is 0, and then returns all of the candidate matches
    one at a time on subsequent calls.

    """

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
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
    readline.parse_and_bind("TAB: menu-complete")
    readline.parse_and_bind('"\\e[B": history-search-forward')
    readline.parse_and_bind('"\\e[A": history-search-backward')
    readline.parse_and_bind('"\\C-l": clear-screen')
    readline.parse_and_bind("set show-all-if-ambiguous on")
    readline.parse_and_bind('"\\C-o": tab-insert')
    readline.parse_and_bind('"\\C-r": reverse-search-history'),
    readline.parse_and_bind('"\\C-s": forward-search-history'),
    readline.parse_and_bind('"\\C-p": "history-search-backward"'),
    readline.parse_and_bind('"\\C-n": "history-search-forward"'),
    readline.parse_and_bind('"\\C-k": "kill-line"'),
    readline.parse_and_bind('"\\C-u": unix-line-discard'),

    readline.read_init_file()
    readline.set_completer(Completer().complete)


def py_readline(rl=None):
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
    rl.read_init_file()
    inputrc = os.environ.get("INPUTRC")
    if inputrc is not None:
        rl.read_inputrc()
    elif os.path.expanduser('~/pyreadlineconfig.ini'):
        rl.read_inputrc(os.path.expanduser('~/pyreadlineconfig.ini'))

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


def teardown_historyfile(histfile=None):
    if not histfile:
        return
    try:
        readline.write_history_file(histfile)
    except OSError:
        logging.error(
            "History not saved. There were problems saving to ~/.python_history"
        )


if __name__ == "__main__":
    # Interestingly this can work on Windows with a simple pip install pyreadline
    # however it can be imported as readline no alias so check it first
    if "pyreadline" in sys.modules:
        pyreadline = sys.modules["pyreadline"]
    else:
        try:
            import readline
        except ImportError:
            raise

    try:
        from pyreadline.rlmain import Readline
        # from pyreadline.lineobj.history import EscapeHistory, LineEditor
        from pyreadline.lineeditor.lineobj import ReadLineTextBuffer
    except (ImportError, ModuleNotFoundError):
        pass
    else:
        readline = Readline()
        py_readline(readline)


    readline_config()
    histfile = "~/.python_history"
    setup_historyfile(histfile)
    atexit.register(teardown_historyfile, histfile)