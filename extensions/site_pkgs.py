#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Show site packages for different virtual environments installed on a system.

Grep Site Packages
==================

Utilize :mod:`IPython` to search through the site-packages directory for
membership of a package.


"""
import argparse
import logging
import os
import sys
from glob import glob
from os.path import expanduser
from os.path import join as pjoin


def _parse_arguments():
    """Parse user input."""
    parser = argparse.ArgumentParser(description="__doc__")

    parser.add_argument(
        "site-packages",
        default=None,
        help="Path to installation-specific site-packages directory.")

    parser.add_argument(
        "-a",
        "--all",
        help="Convenience function that prints all site packages in"
        " ~/virtualenvs",
        dest='all',
        metavar='all',
    )  # gonna need a path to the venv dir

    # Stolen from argparse lib ref.
    parser.add_argument(
        '-l',
        '--log',
        metavar='logfile',
        default=sys.stdout,
        type=argparse.FileType('w'),
        help='The file where the packages should be written. Defaults to'
        ' stdout.')

    parser.add_argument('-ll',
                        '--log-level',
                        metavar='log-level',
                        default=logging.WARNING,
                        type=int,
                        help='Log level. Defaults to logging.WARNING.')

    return parser


def all_site_pkgs():
    """Display every package in site-packages.

    .....wow. This is uh something else.
    *sigh*

    Alright so we gotta make a variable with a sane default for where we're
    checking things. Hopefully sys.executable or sys.prefix...*or is it
    sys.base_prefix?* will lead us in the right direction.

    Then we'll check that the user gave us the right # of arguments with
    len(sys.argv) and ``raise IndexError`` if we get something weird.

    Possibly wanna think about standardizing something for argparse.
    Definitely wanna think about standardizing something for logging.

    Also literally what is that return value??? You didn't use it anywhere.
    Man this is crazy confusing and it shouldn't have been a particularly hard
    thing to write.

    Delete all this off and use pathlib and i suppose build in a sys.version_info
    check as a result.
    """
    home = expanduser('~')

    search = glob(
        pjoin(home, "virtualenvs", "**", "lib", "python3.6", "site-packages",
              "**"))

    for i in search:
        if "dist-info" not in i:
            if os.path.isdir(i):  # don't print loose files
                print(i)
    return pkgs


if __name__ == "__main__":
    parser = _parse_arguments()
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()
    pkgs = all_site_pkgs()  # leave it in user_ns in case I want it for later.

    args.log.write('%s' % pkgs)
    args.log.close()
