#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from git import Git
except:
    Git = None
    Repo = None
else:
    from git import Repo


def git_cur_branch():
    """Return the 'stdout' atribute of a `subprocess.CompletedProcess` checking what the branch of the repo is."""
    try:
        return subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout
    except subprocess.CalledProcessError:
        raise

def git_root():
    try:
        return subprocess.run(["git", "rev-parse", "--show-toplevel"]).stdout
    except subprocess.CalledProcessError:
        raise


def dynamic_ipython_root():
    return git_root()


def dynamic_ipython():
    if Git is not None:
        return Git(dynamic_ipython_root())


