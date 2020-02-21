#!/usr/bin/env python
import sqlite3
import sys
import pprint
import os

from IPython.core.getipython import get_ipython
from IPython.core.history import HistoryAccessor
from IPython.utils.path import get_ipython_dir


def print_history(hist_file):
    with sqlite3.connect(hist_file) as con:
        c = con.cursor()
        c.execute(
            "SELECT count(source_raw) as csr,\
                  source_raw FROM history\
                  GROUP BY source_raw\
                  ORDER BY csr"
        )
        result = c.fetchall()
        pprint.pprint(result)
        c.close()


def get_history():
    session_number = int(sys.argv[1])
    if len(sys.argv) > 2:
        dest = open(sys.argv[2], "w")
        raw = not sys.argv[2].endswith(".py")
    else:
        dest = sys.stdout
        raw = True

    with dest:
        dest.write("# coding: utf-8\n")

        # Profiles other than 'default' can be specified here with a profile= argument:
        hist = HistoryAccessor()

        for session, lineno, cell in hist.get_range(session=session_number, raw=raw):
            cell = cell.encode("utf-8")  # This line is only needed on Python 2.
        dest.write(cell + "\n")


def history_printer():
    """Another way of doing it."""
    hist_file = "%s/profile_default/history.sqlite" % get_ipython_dir()

    if os.path.exists(hist_file):
        print_history(hist_file)
