#!/usr/bin/env python
r"""Extract a session from the IPython input history.

Usage
-----
.. program:: ipython_get_history

  ipython-get-history.py sessionnumber [outputfile]

If outputfile is not given, the relevant history is written to stdout. If
outputfile has a .py extension, the translated history (without IPython's
special syntax) will be extracted.

Example:
  ./ipython-get-history.py 57 record.ipy


This script is a simple demonstration of HistoryAccessor. It should be possible
to build much more flexible and powerful tools to browse and pull from the
history database.

Todo
----

Uh this is just about as annoying as it gets.


.. ipython::
    :okexcept:

    PS C:\Users\faris\src\ipython\examples\kernel> python .\ipython-get-history.py

    Traceback (most recent call 
    last):                                                                                                                

    File ".\ipython-
    get-history.py", line 23, in <module>                                                                                             
    
    session_number = int(sys.argv[1])

    IndexError: list index out of range

    PS C:\Users\faris\src\ipython\examples\kernel> python .\ipython-get-history.py 0

    # coding: utf-8

    PS C:\Users\faris\src\ipython\examples\kernel> python .\ipython-get-history.py 1

    # coding: utf-8

    Traceback (most recent call last):

    File ".\ipython-get-history.py", line 39, in <module>
    dest.write(cell + '\n')
    TypeError: can't concat str to bytes


"""
import sys

from IPython.core.history import HistoryAccessor

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
