#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implement a few magics so as to modify the user's environment."""
import os
from pathlib import Path

from IPython.core.magic import line_magic, Magics, magics_class

# from IPython.core.magic_arguments import magics_class

# from IPython.core.magic_arguments import magics_class


@magics_class
class EnvironMagics(Magics):
    """
    Any class that subclasses Magics *must* also apply this decorator, to
    ensure that all the methods that have been decorated as line/cell magics
    get correctly registered in the class instance.  This is necessary because
    when method decorators run, the class does not exist yet, so they
    temporarily store their information into a module global.  Application of
    this class decorator copies that global data to the class instance and
    clears the global.

    Obviously, this mechanism is not thread-safe, which means that the
    *creation* of subclasses of Magic should only be done in a single-thread
    context.  Instantiation of the classes has no restrictions.  Given that
    these classes are typically created at IPython startup time and before user
    application code becomes active, in practice this should not pose any
    problems.
    """

    @line_magic
    def touch(self, f):
        if f.endswith("py"):
            return Path(f).touch(mode=0o755)
        else:
            return Path(f).touch()

    @line_magic
    def unset(self, arg):
        return os.environ.unset(arg)
