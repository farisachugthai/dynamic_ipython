#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Let's try setting up readline.

Reimplementing Readline
========================

Unsure of how pronounced the effect is going to be since IPython has
prompt_toolkit for most readline features and basic movement bindings
seem to work just fine.

Ooo also I want to reimplement jedi as the completer because IPython's is
confusingly slow.


IPython Custom Completers
-------------------------

.. ipython::
   :verbatim:

    In [69]: _ip.set_custom_completer?
    Signature: _ip.set_custom_completer(completer, pos=0)
    Docstring:
    Adds a new custom completer function.

    The position argument (defaults to 0) is the index in the completers
    list where you want the completer to be inserted.


.. todo:: Shoot all of these functions depend on readline existing so nothing
          can be imported. They should be methods in a class so that we
          know that we have that state pre-established right?

"""
import atexit
import logging
import os
from pathlib import Path
import platform
import rlcompleter
from rlcompleter import Completer

try:
    import readline
except ImportError:
    pass

from IPython.core.getipython import get_ipython

from default_profile.util.module_log import betterConfig


if os.environ.get("IPYTHONDIR"):
    LOG_FILENAME = os.path.join(os.environ.get("IPYTHONDIR"), "completer.log")
    logging.basicConfig(
        format="%(message)s", filename=LOG_FILENAME, level=logging.DEBUG,
    )
else:
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)


def bind_readline_keys():
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\\e[B": history-search-forward')
    readline.parse_and_bind('"\\e[A": history-search-backward')


def read_inputrc():
    """Check for an inputrc file."""
    if os.environ.get("INPUTRC"):
        readline.read_inputrc_file(os.environ.get("INPUTRC"))
    elif Path("~/pyreadlineconfig.ini").is_file():
        readline.read_inputrc_file(str(Path("~/pyreadlineconfig.ini")))
    elif Path("~/.inputrc").is_file():
        readline.read_inputrc_file(os.expanduser("~/.inputrc"))


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
    """
    todo:

        # Register the completer function
        # OPTIONS = ['start', 'stop', 'list', 'print']
        # readline.set_completer(SimpleCompleter(OPTIONS).complete)
        # TODO: Check what the API is to add a completer to ipython. _ip.add_completer?
    """
    line = ""
    while line != "stop":
        line = input('Prompt ("stop" to quit): ')
        print("Dispatch {}".format(line))


def return_readline():
    try:
        import readline
    except (ImportError, ModuleNotFoundError):
        # Interestingly this can work on Windows with a simple pip install pyreadline
        try:
            import pyreadline as readline
        except (ImportError, ModuleNotFoundError):
            logging.warning("Readline not imported.")
            raise
        else:
            from pyreadline.rlmain import Readline

            rl = Readline()
            # So apparently readline.rl in the pyreadline module is an instantiated rlcompleter?
            readline.set_completer(readline.rl.complete)
            return readline
    else:
        return readline


# History


def setup_historyfile(filename=None):
    """Add a history file to readline."""
    if not hasattr(locals(), "readline"):
        readline = return_readline()
    if filename is None:
        filename = "~/.pdb_history"
    histfile = os.path.expanduser(filename)
    try:
        readline.read_history_file(filename)
    except OSError:
        pass
    else:
        readline.set_history_length(200)


def teardown_historyfile(histfile=None):
    """Can we cascade atexit calls like this?"""
    if not histfile:
        return
    if not Path(histfile).exists():
        Path(histfile).expanduser().touch()
    try:
        readline.write_history_file(histfile)
    except OSError:
        logging.error(
            "History not saved. There were problems saving to ~/.python_history"
        )


def jedi_readline():
    try:
        import jedi
    except (ImportError, ModuleNotFoundError):
        jedi = None
    else:
        from jedi.utils import setup_readline

        setup_readline()
        jedi.settings.add_bracket_after_function = False
        # jedi.settings


if __name__ == "__main__":
    jedi_readline()
    readline = return_readline()
    if getattr(readline, "parse_and_bind", None):
        bind_readline_keys()
    if getattr(readline, "read_inputrc_file", None):
        read_inputrc()

    readline.set_completer_delims(" \t\n`@#$%^&*()=+[{]}\\|;:'\",<>?")
    readline.set_completer(Completer().complete)

    # history
    histfile = "~/.python_history"
    # Fallback to the stdlib readline completer if it is installed.
    # Taken from http://docs.python.org/2/library/rlcompleter.html
    setup_historyfile(histfile)
    atexit.register(teardown_historyfile, histfile)
