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


In [69]: _ip.set_custom_completer?
Signature: _ip.set_custom_completer(completer, pos=0)
Docstring:
Adds a new custom completer function.

The position argument (defaults to 0) is the index in the completers
list where you want the completer to be inserted.


"""
import logging
import os
from pathlib import Path
import platform


def readline_logging():
    if os.environ.get("IPYTHONDIR"):
        LOG_FILENAME = os.path.join(os.environ.get("IPYTHONDIR"), "completer.log")
    # else:
    # todo

    logging.basicConfig(
        format="%(message)s", filename=LOG_FILENAME, level=logging.DEBUG,
    )


try:
    import jedi
except (ImportError, ModuleNotFoundError):
    jedi = None
else:
    from jedi.utils import setup_readline

    setup_readline()
    jedi.settings.add_bracket_after_function = False
    # jedi.settings

# Only works inside of xonsh

# try:
#     import xonsh
# except (ImportError, ModuleNotFoundError):
#     xonsh = None
# else:
#     from xonsh.completer import setup_readline
#     setup_readline()


def get_readline():
    # Fallback to the stdlib readline completer if it is installed.
    # Taken from http://docs.python.org/2/library/rlcompleter.html
    try:
        # Interestingly this can work on Windows with a simple pip install pyreadline
        from pyreadline import rlmain

        readline = rlmain.Readline()
    except (ImportError, ModuleNotFoundError):
        try:
            import readline
        except (ImportError, ModuleNotFoundError):
            readline = None
        else:
            return readline
    else:
        return readline


def bind_readline_keys():
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\\e[B": history-search-forward')
    readline.parse_and_bind('"\\e[A": history-search-backward')


def read_inputrc():
    """Check for an inputrc file."""
    if os.environ.get("INPUTRC"):
        readline.read_init_file(os.environ.get("INPUTRC"))


class SimpleCompleter:
    """
    :URL: https://pymotw.com/3/readline/

    The SimpleCompleter class keeps a list of “options” that are candidates
    for auto- completion. The complete() method for an instance is designed
    to be registered with readline as the source of completions.

    The arguments are a text string to complete  and a state value,
    xindicating how many times the function has been called with the
    same text. The function is called repeatedly with the state incremented each time. It
    should return a string if there is a candidate for that state value or None if there
    are no more candidates. The implementation of complete() here looks for a set of
    matches when state is 0, and then returns all of the candidate matches one at a time
    on subsequent calls.
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
    line = ""
    while line != "stop":
        line = input('Prompt ("stop" to quit): ')
        print("Dispatch {}".format(line))


# Register the completer function
# OPTIONS = ['start', 'stop', 'list', 'print']
# readline.set_completer(SimpleCompleter(OPTIONS).complete)


if __name__ == "__main__":
    # Do this part first
    readline_logging()

    # Oddly enough this is available on every platform
    import rlcompleter

    readline = get_readline()

    if hasattr(readline, "read_init_file"):
        bind_readline_keys()
        read_inputrc()

    # TODO: Check what the API is to add a completer to ipython. _ip.add_completer?
