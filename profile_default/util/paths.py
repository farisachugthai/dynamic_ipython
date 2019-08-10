

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
    if isinstance(root, str):
        root = Path(root)

    # TODO: Should probably add one in for bytes
    if root.joinpath(suffix).exists():
        new = root.joinpath(suffix)
        return new
    else:
        DOCS_LOGGER.error('%s: does not exist. Returning None.' % root)
class PathValidator():
    """A simpler and easier way to view the PATH env var on Windows. Work with Unix as well."""
    def __init__(self):
        """Initialize with parameters. Which parameters though?"""
        self.env = dict(os.environ.copy())
        
    def __repr__(self):
        """TODO. If you run the following nothing displays.
        
        Examples
        --------
        >>> PathValidator()
        
        """
        return ''.format(self.__class__.__name__)

    @property
    def path(self):
        """Break the path up into a list and replace the double back slashes."""
        if platform.system()=='Windows':
            return self.env["PATH"].replace('\\', '/').split(';')
        else:
            return self.env["PATH"].split(':')
            
