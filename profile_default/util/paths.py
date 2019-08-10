

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
