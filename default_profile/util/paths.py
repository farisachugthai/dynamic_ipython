#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module for working with paths regardless of platform."""
import logging
import os
import platform
from pathlib import Path

# A) I wanna see if relative imports are working
# B) This would probably make more sense here

from default_profile.util.machine import Platform

logging.BASIC_FORMAT = "%(created)f  %(module)s  %(levelname)s  %(message)s"

PATHS_LOGGER = logging.getLogger(name="default_profile.util").getChild("paths")
PATHS_LOGGER.setLevel(logging.WARNING)


def _path_build(root, suffix):
    """Join parts of paths together and ensure they exist.

    Log nonexistant paths.

    Parameters
    ----------
    root : str or bytes (path-like)
        Directory to build on
    suffix : str, bytes (Path-like)
        What to add to the root directory

    Returns
    -------
    new : Path
        Path object with suffix joined onto root.

    """
    try:
        root = Path(root) if Path(root).exists() else None
    except OSError:
        return
    if root is None:
        return

    # TODO: Should probably add one in for bytes
    if root.joinpath(suffix).exists():
        new = root.joinpath(suffix)
        return new
    else:
        PATHS_LOGGER.error("%s: does not exist. Returning None." % root)


class PathValidator:
    r"""A simpler and easier way to view the :envvar:`PATH` env var on Windows.

    Work with Unix as well.

    .. todo:: Reassigning the var programatically.

        Do we have to escape all the folders with white space like
        C:\\Program Files\\ and their ilk?

    """

    def __init__(self):
        self.env = dict(os.environ.copy())

    def __repr__(self):
        """TODO. If you run the following nothing displays.

        Examples
        --------
        >>> from default_profile.util.paths import PathValidator
        >>> PathValidator()

        """
        return "{}\t{}".format(self.__class__.__name__, self.path)

    @property
    def OS(self):
        return platform.system().lower()

    @property
    def _is_win(self):
        return self.OS == "windows"

    @property
    def path(self):
        """Break the path up into a list and replace the double back slashes."""
        if self._is_win:
            return self.env["PATH"].replace("\\", "/").split(";")
        else:
            return self.env["PATH"].split(":")

    def __call__(self):
        return self.path
