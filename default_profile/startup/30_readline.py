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
    import jedi
except (ImportError, ModuleNotFoundError):
    # Fallback to the stdlib readline completer if it is installed.
    # Taken from http://docs.python.org/2/library/rlcompleter.html
    try:
        # Interestingly this can work on Windows with a simple pip install pyreadline
        import pyreadline as readline
    except (ImportError, ModuleNotFoundError):
        try:
            import readline
        except (ImportError, ModuleNotFoundError):
            pass
        else:
            readline.parse_and_bind("tab: complete")
    else:
        readline.parse_and_bind("tab: complete")

        import rlcompleter
else:
    from jedi.utils import setup_readline
    setup_readline()
    jedi.settings.add_bracket_after_function = True
    jedi.settings
