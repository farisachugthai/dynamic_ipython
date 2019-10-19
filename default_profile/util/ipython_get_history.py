#!/usr/bin/env python3
r"""Extract a session from the IPython input history.

Usage
-----
.. program:: ipython_get_history.py sessionnumber [outputfile]

If 'outputfile' is not given, the relevant history is written to
:data:`sys.stdout.` If 'outputfile' has a *.py* extension,
the translated history (without IPython's special syntax) will be extracted.


Examples
--------

.. code-block:: bash

  python3 ipython-get-history.py 57 record.ipy

This script is a simple demonstration of
:class:`IPython.core.history.HistoryAccessor`. It should be possible
to build much more flexible and powerful tools to browse and pull from the
history database.

So this is a rewrite of that history accessor since IPython's handling of
history sessions out of the box is oddly limited.

Let's ignore the direct calls to sys.argv and combine argparse and the
magic_argparse functions to make something more durable and useful.

"""
import sys

from IPython.core.history import HistoryAccessor


def get_history():
    """TODO: Docstring for main.

    Parameters
    ----------
    arg1 : TODO

    Returns
    -------
    TODO

    """
    session_number = int(sys.argv[1])
    if len(sys.argv) > 2:
        dest = open(sys.argv[2], "w")
        raw = not sys.argv[2].endswith('.py')
    else:
        dest = sys.stdout
        raw = True

    with dest:
        dest.write("# coding: utf-8\n")

        # Profiles other than 'default' can be specified here with a profile= argument:
        hist = HistoryAccessor()

        for session, lineno, cell in hist.get_range(session=session_number, raw=raw):
            cell = cell.encode('utf-8')  # This line is only needed on Python 2.
        dest.write(cell + '\n')


if __name__ == "__main__":
    sys.exit(main())
