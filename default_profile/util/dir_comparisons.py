#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility functions for comparing directories."""
from filecmp import dircmp


def print_diff_files(dcmp):
    """Example of how to utilize `dircmp`."""
    for name in dcmp.diff_files:
        print("diff_file %s found in %s and %s" %
              (name, dcmp.left, dcmp.right))
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)
        yield sub_dcmp


def print_diff_dirs(dir_a, dir_b):
    """With the right # args this time."""
    diffed = dircmp(dir_a, dir_b)
    print_diff_files(diffed)
    return diffed
