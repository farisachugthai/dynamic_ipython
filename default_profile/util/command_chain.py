#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Redo the CommandChainDispatcher in IPython.core.hooks for more flexbility."""
from pprint import pprint
from reprlib import Repr
import sys
from typing import TYPE_CHECKING

import IPython
from IPython.core.getipython import get_ipython
from IPython.utils.ipstruct import Struct
from traitlets.traitlets import Instance

import functools
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import types

from contextlib import ContextDecorator, contextmanager
from subprocess import DEVNULL, PIPE, CalledProcessError, CompletedProcess, Popen
from typing import get_type_hints, TYPE_CHECKING
from pathlib import Path

from prompt_toolkit.application.run_in_terminal import run_in_terminal
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, ViInsertMode, EmacsInsertMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import print_formatted_text as print
from prompt_toolkit.utils import Event


if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShellABC


@contextmanager
def inside_dir(dirpath):
    """Context manager that executes code from inside the given directory.

    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


def run_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the exit status.

    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(
            shlex.split(shlex.quote(command)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def check_output_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the command output.

    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.run(
            shlex.split(shlex.quote(command)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


class Executable(ContextDecorator):
    """An object representing some executable on a user computer."""

    def __init__(self, command):
        """Initialize with *command*."""
        self.command = command
        self.command_path = self._get_command_path(command)
        super().__init__()

    @property
    def _command(self):
        return self.command

    def _get_command_path(self, command):
        """Return the path to an executable if *command* is on `PATH`.

        Same signature as :func:`shutil.which`.

        Returns
        -------
        str (path-like)
            Path to an executable if it's found. Otherwise `None`.

        """
        return shutil.which(command)

    def __repr__(self):
        return "Executable: {!r}".format(self.command)

    def __call__(self, *args, **kwargs):
        if self.command_path is not None:

            @functools.wraps
            def wrapped(*args, **kwargs):
                return subprocess.run(
                    ["bash", "-c", self.command_path(), *args], **kwargs
                )

            return wrapped(*args, **kwargs)


def is_tmux():
    """Check if we're using tmux or not."""
    if os.environ.get("TMUX"):
        return True


def is_rg():
    """Returns the path to rg."""
    return shutil.which("rg")


class CommandChainDispatcherRepr(Struct):
    """Subclass IPython's Struct to allow for more functionality.

    Methods
    -------
    Refer to the superclass for most methods.
    Simply, all I've done here is to remove the double underscore from most
    methods to improve visibility.

    """

    # .. todo:: collection.ChainMap?

    shell = Instance("IPython.core.interactiveshell.InteractiveshellABC")

    def __init__(self, shell=None, chain=None, level=6, *args, **kwargs):
        """Initialize the class.

        Parameters
        ----------
        shell : :class:`~IPython.core.interactiveshell.InteractiveShell`
            IPython instance.
        chain : dict
            IPython hooks.
        level : int
            Passed to `reprlib.Repr` for processing visual representation.
        """
        self.shell = shell or get_ipython()
        super().__init__(self.shell, **kwargs)

        # self.chain might work really well as a queue.PriorityQueue
        if self.shell is not None:
            self.chain = self.shell.hooks
        else:
            self.chain = chain or {}

        self.level = level

    def __repr__(self):
        return Repr().repr(self.chain)

    def add(self, other):
        self.__add__(other)

    def iadd(self, other):
        self.__iadd__(other)

    def __str__(self):
        """If someone calls print() they actually want to see the instance's hooks."""
        pprint(self.chain)
        return self.chain

    def __sizeof__(self):
        """Implement sizeof to see how much the extra methods cost us."""
        return object.__sizeof__(self) + sum(
            sys.getsizeof(v) for v in self.__dict__.values()
        )


