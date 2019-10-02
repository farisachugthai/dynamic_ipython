#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Let's try setting up readline.

Unsure of how pronounced the effect is going to be since IPython has
prompt_toolkit for most readline features and basic movement bindings
seem to work just fine.

Ooo also I want to reimplement jedi as the completer because IPython's is
confusingly slow.
"""
try:
    from jedi.utils import setup_readline
    setup_readline()
except ImportError:
    # Fallback to the stdlib readline completer if it is installed.
    # Taken from http://docs.python.org/2/library/rlcompleter.html
    print("Jedi is not installed, falling back to readline")
    try:
        # Interestingly this can work on Windows with a simple pip install pyreadline
        import readline
        import rlcompleter
        readline.parse_and_bind("tab: complete")
    except ImportError:
        print("Readline is not installed either. No tab completion is enabled.")
