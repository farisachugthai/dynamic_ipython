#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module where readline is properly configured before prompt_toolkit is loaded.

Summary
-------

Readline is implemented in the repository for a few reasons.

#) It's ubiquity in open source programming

#) In addition, it's utilized here to compensate for the weaknesses of other
   implementations.

   #) IPython's auto-completion is entirely unconfigurable and exceedingly slow

      #) Frequently auto-completion will time out rather than serving a response

   #) `prompt_toolkit` has a rather rigid interface for it's API. There are
      assert's all over the code base ensuring that the proper type is passed
      to a class constructer, in spite of the Python's dynamically typed
      foundation.

Extended Summary
----------------

.. did you know that this is a numpydoc header? lol

This module assumes


"""
import atexit
import logging
import os
from pathlib import Path
import platform
import rlcompleter
from rlcompleter import Completer
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


def readline_config(history_file=None):
    """The main point of execution for the readline module.

    This sets up history where the history file is saved to and calls
    `atexit` with the `setup_historyfile` and `teardown_historyfile` functions
    as parameters.

    Parameters
    ----------
    history_file : str, path or `os.Pathlike`
        Where to save the history

    """
    histfile = "~/.python_history"
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\\e[B": history-search-forward')
    readline.parse_and_bind('"\\e[A": history-search-backward')

    setup_historyfile(histfile)
    atexit.register(teardown_historyfile, histfile)

    # Check for an inputrc file.
    if os.environ.get("INPUTRC"):
        readline.read_inputrc_file(os.environ.get("INPUTRC"))
    elif Path("~/pyreadlineconfig.ini").is_file():
        readline.read_inputrc_file(str(Path("~/pyreadlineconfig.ini")))
    elif Path("~/.inputrc").is_file():
        readline.read_inputrc_file(os.expanduser("~/.inputrc"))
    readline.set_completer_delims(" \t\n`@#$%^&*()=+[{]}\\|;:'\",<>?")
    readline.set_completer(Completer().complete)

    readline.read_init_file()

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
            logging.exception('Could not create the history file.')

    histfile_str = str(histfile)
    try:
        readline.read_history_file(histfile_str)
    except OSError as e:
        logging.exception('Could not read the history file.')
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
    try:
        import readline
    except (ImportError, ModuleNotFoundError):
        # Interestingly this can work on Windows with a simple pip install pyreadline
        try:
            import pyreadline as readline
        except (ImportError, ModuleNotFoundError):
            logging.warning("Readline not imported.")
            raise

    readline_config()
