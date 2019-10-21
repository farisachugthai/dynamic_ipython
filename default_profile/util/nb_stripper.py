#!/usr/bin/env python3
"""Strip outputs from an IPython Notebook.

Opens a notebook, strips its output, and overwrites the original file.

Useful as a :command:`git` filter or pre-commit hook for users who don't want to track output in VCS.

This does mostly the same thing as the `Clear All Output` command in the notebook UI.

"""
import io
import sys

try:
    # Jupyter >= 4
    from nbformat import read, write, NO_CONVERT
except ImportError:
    # IPython 3
    try:
        from IPython.nbformat import read, write, NO_CONVERT
    except ImportError:
        # IPython < 3
        from IPython.nbformat import current

        def read(f, as_version):
            return current.read(f, 'json')

        def write(nb, f):
            return current.write(nb, f, 'json')


def _cells(notebook):
    """Yield all cells in an nbformat-insensitive manner.

    Parameters
    ----------
    notebook : str (path-like)
        Path to notebook

    Yields
    ------
    cell

    """
    if notebook.nbformat < 4:
        for ws in notebook.worksheets:
            for cell in ws.cells:
                yield cell
    else:
        for cell in notebook.cells:
            yield cell


def strip_output(nb):
    """strip the outputs from a notebook object."""
    nb.metadata.pop('signature', None)
    for cell in _cells(nb):
        if 'outputs' in cell:
            cell['outputs'] = []
        if 'prompt_number' in cell:
            cell['prompt_number'] = None
    return nb


def main():
    """Strip output from a user's notebook."""
      filename = sys.argv[1]
       with io.open(filename, 'r', encoding='utf8') as f:
            nb = read(f, as_version=NO_CONVERT)
        nb = strip_output(nb)
        with io.open(filename, 'w', encoding='utf8') as f:
            write(nb, f)


if __name__ == '__main__':
    sys.exit(main())

