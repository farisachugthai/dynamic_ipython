"""Rewrite the IPython ProfileDir.

Profile Override
================

Override the IPython ProfileDir.

Initially created to implement a repr for the class, it was expanded in order
to also modify the behavior that automatically adds a PID dir,

It automatically creates them in the current working directory and this
behavior was not designed to be modifiable.

As a result, profiles are frequently created in the
wrong dir often enough that it should be toggleable behavior.

See Also
--------

:mod:`IPython.core.profileapp`.

"""
import errno
import os
import shutil
import sys
from pathlib import Path
from traceback import print_exc

from IPython.core.getipython import get_ipython
from IPython.core.profiledir import ProfileDir
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.ipapp import TerminalIPythonApp

# from IPython.paths import ensure_dir_exists, get_ipython_package_dir
from traitlets.config import Bool, Unicode, observe
from traitlets.traitlets import TraitError


class ProfileDirError(Exception):
    pass


class ReprProfileDir(ProfileDir):
    """An object to manage the profile directory and its resources.

    The profile directory is used by all IPython applications, to manage
    configuration, logging and security.

    This object knows how to find, create and manage these directories. This
    should be used by any code that wants to handle profiles.
    """

    def __init__(self, *args, **kwargs):
        """Create an init and then make it way shorter."""
        super().__init__(**kwargs)
        self.ensure_dir_exists = DirectoryChecker
        startup_dir = Unicode("startup")
        log_dir = Unicode("log")
        location = Unicode(
            help="""Set the profile location directly. This overrides the logic used by the
            `profile` option.""",
            allow_none=True,
        ).tag(config=True)

    # don't set the location more than once no matter how many profiles
    # are instantiated so yes a class attr
    _location_isset = False

    def __repr__(self):
        """I'll admit this is unnecessary. Oh well."""
        return "{}: {}".format(self.__class__.__name__, self.location)

    @observe("location")
    def _location_changed(self, change):
        """This is so odd to me. What is change when does it get called?

        Raises
        ------
        TraitError
            No longer raises RuntimeError because that's insane

        """
        if self._location_isset:
            raise TraitError("Cannot set profile location more than once.")
        self._location_isset = True
        new = change["new"]
        self.ensure_dir_exists()

        # what is static?
        for i in ["security", "log", "startup", "pid", "static"]:
            self.ensure_dir_exists()

    def ensure_dir_exists(self, folder):
        if not hasattr(folder, "exists"):
            folder = Path(folder)
        if not folder.exists():
            try:
                folder.mkdir()
            except PermissionError:
                return errno.EPERM
            except FileExistsError:
                raise
            # except IsADirectoryError:
            # Do we need to catch this?


class DirectoryChecker:
    """Let's redo profiledir with pathlib.

    Dude we're allowed to subclass os.Pathlike. I wonder if that'd make this
    easier.
    """

    def __init__(self):
        """Initialize our own version of ipython."""
        self.fs = Path

    @property
    def shell(self):
        return get_ipython()

    def initialize(self):
        """TODO: Add getattr checks for this func so we don't call on an uninitialized object."""
        if self.shell.initialized():
            # Running inside IPython

            # Detect if embed shell or not and display a message
            if isinstance(self.shell, InteractiveShellEmbed):
                sys.stderr.write(
                    "\nYou are currently in an embedded IPython shell,\n"
                    "the configuration will not be loaded.\n\n"
                )
        else:
            # Not inside IPython
            # Build a terminal app in order to force ipython to load the configuration
            ipapp = TerminalIPythonApp()
            # Avoid output (banner, prints)
            ipapp.interact = False

    @staticmethod
    def ensure_dir_exists(path, mode=0o755):
        """Ensure that a directory exists.

        If it doesn't exist, try to create it and protect against a race
        condition if another process is doing the same.

        The default permissions are :data:`0o755`, which differ from
        :func:`os.makedirs()` default of :data:`0o777`.

        Parameters
        ----------
        path : str (path-like)
            Path to the directory
        mode : int
            If the directory doesn't exist, what mode should it be created as?

        Returns
        -------
        None

        Raises
        ------
        OSError, IOError

        """
        if not os.path.exists(path):
            try:
                os.makedirs(path, mode=mode)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        elif not os.path.isdir(path):
            raise IsADirectoryError("%r exists but is not a directory" % path)

    def initialize_profile(self):
        """Initialize the profile but sidestep the IPython.core.ProfileDir().

        The class searches for directories named default_profile and if found
        uses that as a profile which I dislike.
        """
        profile_to_load = Path("~/.ipython/default_profile")

        try:
            self.ensure_dir_exists(profile_to_load)
        except OSError as e:
            print_exc(e)
        else:
            self.shell.profile_dir = os.path.expanduser("~/.ipython/default_profile")
