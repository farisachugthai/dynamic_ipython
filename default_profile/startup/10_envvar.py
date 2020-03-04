#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implement a few magics so as to modify the user's environment."""
import contextlib
import os
import sys
from _io import (
    DEFAULT_BUFFER_SIZE,
    BlockingIOError,
    UnsupportedOperation,
    BufferedRWPair,
    BufferedWriter,
    BufferedReader,
    TextIOWrapper,
)
# from io import RawIOBase
from pathlib import Path

from IPython.core.magic import line_magic, Magics, magics_class


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

    @line_magic
    def symlink(self, dest, source=None):
        pass


class DevNull(TextIOWrapper):
    """The standard library implements a version of os.devnull.

    Surprisingly, that implementation equates it to a string, and as a result
    the expression, ``sys.stdout = os.devnull``, will crash the interpreter.
    """

    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    def __init__(self, new_stdout=None, *args, **kwargs):
        """If stdout is None, redirect to /dev/null"""
        self._new_stdout = new_stdout or open(os.devnull, "w")
        self.reader = self._reader()
        self.writer = self._writer()
        self._buffer = self._bufferedrw()
        super().__init__(buffer=self._buffer, *args, **kwargs)

    def __enter__(self):
        sys.stdout.reconfigure(line_buffering=True)  # implies flush
        self.oldstdout_fno = os.dup(sys.stdout.fileno())
        os.dup2(self._new_stdout.fileno(), 1)

    def __exit__(self, exc_type, exc_value, traceback):
        self._new_stdout.flush()
        os.dup2(self.oldstdout_fno, 1)
        os.close(self.oldstdout_fno)

    def _reader(self):
        return BufferedReader(sys.stdin)

    def _writer(self):
        return BufferedWriter(sys.stdout)

    def _bufferedrw(self):
        return BufferedRWPair(self.reader, self.writer, DEFAULT_BUFFER_SIZE)


@contextlib.contextmanager
def stdout(self):
    try:
        self = sys.stdout
    finally:
        sys.stdout = original_stdout
