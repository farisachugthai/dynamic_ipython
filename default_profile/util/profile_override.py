"""
Profile Override
================

Override the IPython ProfileDir().

It feels rude to do it this way but all I wanna do is add a repr! Oh I guess I
could just inherit everything from this class.

Eh. I also wanna modify the behavior that automatically adds a PID dir, security dir, etc.

I get why it's difficult to run it selectively but it automatically creates them in the wrong dir
often enough that it should be toggleable behavior.

See Also
--------
.. seealso::

    :mod:`IPython.core.profileapp`.


"""
import errno
import os
import shutil
from pathlib import Path

from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.ipapp import TerminalIPythonApp

# from IPython.paths import ensure_dir_exists, get_ipython_package_dir
from traitlets.config import Bool, LoggingConfigurable, Unicode, observe


class ProfileDirError(Exception):
    """Foo."""
    pass


class ReprProfileDir(LoggingConfigurable):
    """An object to manage the profile directory and its resources.

    The profile directory is used by all IPython applications, to manage
    configuration, logging and security.

    This object knows how to find, create and manage these directories. This
    should be used by any code that wants to handle profiles.
    """

    def __init__(self, *args, **kwargs):
        """Create an init and then make it way shorter."""
        super().__init__(*args, **kwargs)
        self.ensure_dir_exists = DirectoryChecker
        startup_dir = Unicode('startup')
        log_dir = Unicode('log')
        location = Unicode(
            help="""Set the profile location directly. This overrides the logic used by the
            `profile` option.""", allow_none=True
        ).tag(config=True)

    # don't set the location more than once no matter how many profiles
    # are instantiated so yes a class attr
    _location_isset = False

    def __repr__(self):
        """I'll admit this is unnecessary. Oh well."""
        return '{}: {}'.format(self.__class__.__name__, self.location)

    @observe('location')
    def _location_changed(self, change):
        """This is so odd to me. What is change when does it get called?"""
        if self._location_isset:
            raise RuntimeError("Cannot set profile location more than once.")
        self._location_isset = True
        new = change['new']
        self.ensure_dir_exists(new)

        # what is static?
        for i in ['security', 'log', 'startup', 'pid', 'static']:
            self.ensure_dir_exists(Path(new, i))

    @observe('pid_dir')
    def check_pid_dir(self, change=None):
        self._mkdir(self.pid_dir, 0o40700)

    def copy_config_file(self, config_file, path=None, overwrite=False):
        """Copy a default config file into the active profile directory.

        Default configuration files are kept in :mod:`IPython.core.profile`.
        This function moves these from that location to the working profile
        directory.
        """
        dst = os.path.join(self.location, config_file)
        if os.path.isfile(dst) and not overwrite:
            return False
        if path is None:
            path = os.path.join(
                get_ipython_package_dir(), u'core', u'profile', u'default'
            )
        src = os.path.join(path, config_file)
        shutil.copy(src, dst)
        return True

    @classmethod
    def create_profile_dir(cls, profile_dir, config=None):
        """Create a new profile directory given a full path.

        Parameters
        ----------
        profile_dir : str
            The full path to the profile directory.  If it does exist, it will
            be used.  If not, it will be created.
        """
        return cls(location=profile_dir, config=config)

    @classmethod
    def create_profile_dir_by_name(cls, path, name=u'default', config=None):
        """Create a profile dir by profile name and path.

        Parameters
        ----------
        path : unicode
            The path (directory) to put the profile directory in.
        name : unicode
            The name of the profile.  The name of the profile directory will
            be "profile_<profile>".

        """
        if not os.path.isdir(path):
            raise ProfileDirError('Directory not found: %s' % path)
        profile_dir = os.path.join(path, u'profile_' + name)
        return cls(location=profile_dir, config=config)

    @classmethod
    def find_profile_dir_by_name(
            cls, ipython_dir, name=u'default', config=None
    ):
        """Find an existing profile dir by profile name, return its ProfileDir.

        This searches through a sequence of paths for a profile dir.  If it
        is not found, a :class:`ProfileDirError` exception will be raised.

        The search path algorithm is:

        1. :func:`os.getcwd`

        2. :envvar:IPYTHONDIR`


        Parameters
        ----------
        ipython_dir : str
            The IPython directory to use.
        name : unicode or str
            The name of the profile.  The name of the profile directory
            will be "profile_<profile>".

        """
        dirname = u'profile_' + name
        paths = [os.getcwd(), ipython_dir]
        for p in paths:
            profile_dir = os.path.join(p, dirname)
            if os.path.isdir(profile_dir):
                return cls(location=profile_dir, config=config)
        else:
            raise ProfileDirError(
                'Profile directory not found in paths: %s' % dirname
            )

    @classmethod
    def find_profile_dir(cls, profile_dir, config=None):
        """Find/create a profile dir and return its ProfileDir.

        This will create the profile directory if it doesn't exist.

        Parameters
        ----------
        profile_dir : unicode or str
            The path of the profile directory.
        """
        profile_dir = expand_path(profile_dir)
        if not os.path.isdir(profile_dir):
            raise ProfileDirError(
                'Profile directory not found: %s' % profile_dir
            )
        return cls(location=profile_dir, config=config)


class DirectoryChecker:
    """Let's redo profiledir with pathlib.

    Dude we're allowed to subclass os.Pathlike. I wonder if that'd make this
    easier.
    """

    def __init__(self, canary=None, *args, **kwargs):
        """Initialize our own version of ipython."""
        if canary is not None:
            self.canary = canary
        else:
            self.canary = get_ipython()
        self.fs = Path

    def initialize(self):
        """TODO: Add getattr checks for this func so we don't call on an uninitialized object."""
        if self.canary.initialized():
            # Running inside IPython

            # Detect if embed shell or not and display a message
            if isinstance(self.canary, InteractiveShellEmbed):
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
                    raise IOError(e)
        elif not os.path.isdir(path):
            raise IOError("%r exists but is not a directory" % path)

    def initialize_profile(self):
        """Initialize the profile but sidestep the IPython.core.ProfileDir().

        The class searches for directories named default_profile and if found
        uses that as a profile which I dislike.
        """
        profile_to_load = Path("~/.ipython/default_profile")

        try:
            self.ensure_dir_exists(profile_to_load)
        except OSError as e:
            print(e)
        else:
            self.canary.profile_dir = os.path.expanduser("~/.ipython/default_profile")
