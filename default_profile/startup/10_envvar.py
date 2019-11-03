#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implement a few magics so as to modify the user's environment."""
import os
from pathlib import Path

from IPython.core.magic import line_magic, Magics, magics_class


@magics_class
class EnvironMagics(Magics):

    @line_magic
    def touch(f):
        if f.endswith('py'):
            return Path(f).touch(mode=0o755)
        else:
            return Path(f).touch()


    @line_magic
    def unset(arg):
        return os.environ.unsetenv(arg)
