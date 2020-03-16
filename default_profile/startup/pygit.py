#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import subprocess
from os import getcwd
from pathlib import Path

try:
    from git import Repo
except:
    Repo = None

# noinspection PyProtectedMember
from pip._internal.vcs.git import Git


class ShellRepo:
    """A class to customize the behavior of Git."""

    def __init__(self, root=None):
        """Set the optional parameter root equal to 'root' or :meth:`git_root`."""
        self.root = root
        if self.root is None:
            self.root = self.git_root()
        self.current_branch = self.git_cur_branch()
        self.logger = logging.getLogger(name=__name__)

    def __repr__(self):
        return f"{self.__class__.__name__}>"

    def git_cur_branch(self):
        """Return the 'stdout' atribute of a `subprocess.CompletedProcess` checking what the branch of the repo is."""
        try:
            return subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout
        except subprocess.CalledProcessError:
            raise

    def git_root(self):
        try:
            root = subprocess.run(["git", "rev-parse", "--show-toplevel"]).stdout
        except subprocess.CalledProcessError:
            raise
        else:
            self.root = root
            return root

    def log(self, msg, log_level=30):
        """Bind a logger to aide debugging."""
        self.logger.log(msg, log_level=log_level)

    def dynamic_ipython(self):
        if Git is not None:
            if not self.root.exists():
                # uhhhhhhh
                self.log.critical(f"{self.root} doesn't exist")
            return Git(self.root())


class PyGit(Git):
    """Subclass pip's Git implementation."""

    def __mro__(self):
        """For `inspect.getmro`."""
        if hasattr(self, "__bases__"):
            return self.__bases__

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def get_current_branch(self, location=None):
        """Make the super classes' *location* parameter optional."""
        if location is None:
            location = getcwd()
        return super().get_current_branch(location)
