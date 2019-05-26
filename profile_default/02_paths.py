#!/usr/bin/env python
"""Override the IPython logic to find the profile dir.

Paths
=====
04/24/2019

.. ipython:: python

    def find_profile_dir_by_name(cls, ipython_dir, name=u'default', config=None):
        # Find an existing profile dir by profile name, return its ProfileDir.

        # This searches through a sequence of paths for a profile dir.  If it
        # is not found, a :class:`ProfileDirError` exception will be raised.

        # The search path algorithm is:
        # 1. ``os.getcwd()``
        # 2. ``ipython_dir``

        # Parameters
        # ----------
        # ipython_dir : unicode or str
        #     The IPython directory to use.
        # name : unicode or str
        #     The name of the profile.  The name of the profile directory
        #     will be "profile_<profile>".
        dirname = u'profile_' + name
        paths = [os.getcwd(), ipython_dir]
        for p in paths:
            profile_dir = os.path.join(p, dirname)
            if os.path.isdir(profile_dir):
                return cls(location=profile_dir, config=config)
        else:
            raise ProfileDirError('Profile directory not found in paths: %s' % dirname)


We override this method in order to avoid sourcing the wrong one simply because
we were in that directory.

Apr 28, 2019

Here's your current traceback. Moved that file out of startup so you can
resume IPython usage as normal.

.. code-block:: python-traceback

    ERROR:root:Profile directory error.
    2019-04-28 01:20:40 [TerminalIPythonApp] WARNING | Unknown error in handling startup files:
    --------------------------------------------------------------
    TypeError   Traceback (most recent call last)
    ~/virtualenvs/dynamic/lib/python3.7/site-packages/IPython/core/shellapp.py in _exec_file(self, fname,
    shell_futures)
    338         self.shell.user_ns,
    339         shell_futures=shell_futures,
    --> 340                   raise_exceptions=True)
    341         finally:
    342             sys.argv = save_argv

    ~/virtualenvs/dynamic/lib/python3.7/site-packages/IPython/core/interactiveshell.py in
    safe_execfile(self, fname, exit_ignore, raise_exceptions, shell_futures, *where)
    2710                 py3compat.execfile(
    2711                                fname, glob, loc,
    -> 2712                             self.compile if shell_futures else None)
    2713             except SystemExit as status:
    2714                 # If the call was made with 0 or None exit status
    (sys.exit(0)

    ~/virtualenvs/dynamic/lib/python3.7/site-packages/IPython/utils/py3compat.py
    in execfile(fname, glob, loc, compiler)
    186     with open(fname, 'rb') as f:
    187         compiler = compiler or compile
    --> 188         exec(compiler(f.read(), fname, 'exec'), glob,
    loc)
    189
    190 # Refactor print statements in doctests.

    ~/.ipython/profile_default/startup/02_paths.py in
    <module>
    114     _ip = get_ipython()
    115     # Is this supposed to be IPythonPath... or IPythonPath()?
    --> 116     _ip.ProfileDir.location =
                        IPythonPath.find_profile_dir_by_name(ipython_root_dir)

    ~/.ipython/profile_default/startup/02_paths.py
    in find_profile_dir_by_name(cls, ipython_dir, name, config)
    103         if dirpath.is_dir:
    104             profile_dir = str(dirpath)
    --> 105             return  cls(location=profile_dir,config=config)
    106         else:
    107             raise ProfileDirError

    TypeError: __init__() got an unexpected keyword argument 'location'


So I don't feel like debugging that right now but that's where we're at.

"""
import logging
import os
import sys
from pathlib import Path

from IPython import get_ipython
# from IPython.paths import get_ipython_dir


def _setup_logging(logger_name=None, logger_format=None, log_handler=None):
    """Initialize a :class:`logging.Logger()`.

    Trying to factor out all of the hard coded nonsense in this function.
    Unfortunately the more the problem gets broken down the farther we sink in.
    """
    if logger_name is None:
        logger = logging.getLogger(name=__name__)

    logger.setLevel(logging.WARNING)

    if log_handler is None:
        handler = logging.StreamHandler(sys.stdout)

    handler.setLevel(logging.WARNING)

    if logger_format is None:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# ----------------------------------------------------------------------------
# Module errors
# ----------------------------------------------------------------------------

class ProfileDirError(Exception):
    logging.error('Profile directory error.')


class PathManagerError(Exception):
    """I have no idea how to do this correctly."""
    PathLogger = _setup_logging()
    PathLogger.error('%s' % sys.traceback)

# ----------------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------------


class IPythonPath(ProfileDir):
    def __init__(self):
        super().__init__()

    @classmethod
    def find_profile_dir_by_name(cls,
                                 ipython_dir: Path,
                                 name: object = u'default',
                                 config: object = None) -> object:
        """Find an existing profile dir by profile name, return its ProfileDir.

         This searches through a sequence of paths for a profile dir.  If it
         is not found, a :class:`ProfileDirError` exception will be raised.

         The search path algorithm WAS:

             1. ``os.getcwd()``
             2. ``ipython_dir``

         Currently it is:

         1. ``ipython_dir``

         The implementation also differs slightly from IPython's in that it
         uses :mod:`pathlib`.

         Parameters
         ----------
         ipython_dir : unicode or str
             The IPython directory to use.
         name : unicode or str
             The name of the profile.  The name of the profile directory
             will be "profile_<profile>".

         Examples
         --------
         ::

        """
        dirname = u'profile_' + name
        ipython_path = Path(ipython_dir)
        dirpath = ipython_path.joinpath(dirname)
        if dirpath.is_dir:
            return str(dirpath)
        else:
            raise ProfileDirError


class PathManager():
    """I think we got it.

    Examples
    --------
    ::

        >>> pm = PathManager()
        >>> ''.join(i for i in dir(pm) if not i.startswith('_'))


    .. ipython:: python

        In [190]: tmp = '\n'.join(i for i in dir(pm) if not i.startswith('_'))
        Out[190]: 'Path\nshell'
        [ins] In [191]: print(tmp)
        Path
        shell


    Parameters
    ----------
    ipython_dir : unicode or str
        The IPython directory to use.
    name : unicode or str
        The name of the profile.  The name of the profile directory
        will be "profile_<profile>".

        """
        dirname = u'profile_' + name
        ipython_path = Path(ipython_dir)
        dirpath = ipython_path.joinpath(dirname)
        if dirpath.is_dir:
            return str(dirpath)
        else:
            raise ProfileDirError

    def __repr__(self):
        return format({i: j for i, j in self.shell.config.items()})

    def __init__(self, shell=None):
        """Initialize an IPython mixin with pathlib."""
        if shell is None:
            self.shell = get_ipython()
        self.Path = Path(self.shell.profile_dir.location)

def get_home():
    """Get the home dir."""
    if os.name == 'Linux':
        return os.path.expanduser('~')
    elif os.name == 'Win32':
        return os.environ.get('USERPROFILE')


if __name__ == '__main__':
    logger = _setup_logging()

    HOME = Path.home()
    ipython_root_dir = Path.joinpath(HOME, '', '.ipython/profile_default')
    _ip = get_ipython()
    # Is this supposed to be IPythonPath... or IPythonPath()?
    _ip.ProfileDir.location = IPythonPath.find_profile_dir_by_name(
        ipython_root_dir)
