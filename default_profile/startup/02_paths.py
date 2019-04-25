"""Override the IPython logic to find the profile dir.

Paths
=====
04/24/2019

.. code-block:: python

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
"""
import logging
import os
from pathlib import Path
import sys

from IPython import get_ipython
from IPython.core.profiledir import ProfileDir

# ----------------------------------------------------------------------------
# Module errors
# ----------------------------------------------------------------------------


def _setup_logging():
    """Enable logging. TODO: Need to add more to the formatter."""
    logger = logging.getLogger(name=__name__)
    logger.setLevel(logging.WARNING)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class ProfileDirError(Exception):
    logging.error('Profile directory error.')


class IPythonPath(ProfileDir):

    def __init__(self):
        super().__init__()

    @classmethod
    def find_profile_dir_by_name(cls, ipython_dir, name=u'default', config=None):
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
        """
        dirname = u'profile_' + name
        ipython_path = Path(ipython_dir)
        dirpath = ipython_path.join(dirname)
        if dirpath.isdir:
            profile_dir = str(dirpath)
            return cls(location=profile_dir, config=config)
        else:
            raise ProfileDirError


if __name__ == '__main__':
    logger = _setup_logging()
    _ip = get_ipython()
    # Is this supposed to be IPythonPath... or IPythonPath()?
    _ip.ProfileDir.location = IPythonPath.find_profile_dir_by_name()
