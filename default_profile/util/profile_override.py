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

    Notes
    -----
    Implements `__fspath__` to implement the pathlib protocol.

    """

    def __init__(self, **kwargs):
        """Create an init and then make it way shorter."""
        super().__init__(**kwargs)
        self.ensure_dir_exists = DirectoryChecker
        # startup_dir = Unicode("startup")
        # log_dir = Unicode("log")
        location = Unicode(
            help="""Set the profile location directly. This overrides the logic used by the
            `profile` option.""",
            allow_none=True,
        ).tag(
            config=True
        )  # noqa

    # don't set the location more than once no matter how many profiles
    # are instantiated so yes a class attr
    _location_isset = False

    def __repr__(self):
        """I'll admit this is unnecessary. Oh well."""
        return "{}: {}".format(self.__class__.__name__, self.location)

    def _mkdir(self, path, mode=0o755):
        """Override the superclasses mkdir."""
        try:
            Path(path).mkdir()
        except OSError as e:
            if e.errno == errno.EEXIST:
                return False
            else:
                raise

    def __fspath__(self):
        return str(self.location)

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


class DirectoryChecker:
    """Checks for the presence of needed directories and creates them."""

    def __init__(self, *args):
        """Initialize with optional needed dirs."""
        self.fs = Path
        self.initialize()

    @property
    def shell(self):
        """Return the global IPython instance."""
        return get_ipython()

    def initialize(self):
        """Initialize with a modified version of the IPython shell."""
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

    def ensure_dir_exists(self, path, mode=0o755):
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
        if not hasattr(folder, "exists"):
            folder = self.fs(folder)
        if not folder.exists():
            try:
                folder.mkdir()
            except PermissionError:
                return errno.EPERM
            except FileExistsError:
                raise
            except IsADirectoryError:
                raise

    def initialize_profile(self):
        """Initialize the profile but sidestep the IPython.core.ProfileDir().

        The class searches for directories named default_profile and if found
        uses that as a profile which I dislike.
        """
        profile_to_load = self.fs("~/.ipython/default_profile").expanduser()

        try:
            self.ensure_dir_exists(profile_to_load)
        except OSError as e:
            print_exc(e)
        else:
            self.shell.profile_dir = os.path.expanduser("~/.ipython/default_profile")
