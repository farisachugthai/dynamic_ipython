#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run rehashx magic.

This is an incredible little gem that's hugely useful for
making IPython work as a more versatile system shell.

The code that's more important than anything should execute regardless
of whether someone has ``pip install``-ed it.

"""
import runpy
from os import scandir

from IPython.core.getipython import get_ipython


def rehashx_run():
    """Add all executables on the user's :envvar:`PATH` into the IPython ns.

    Parameters
    ----------
    shell : |ip| instance
        IPython shell instance.

    """
    _ip = get_ipython()
    if _ip is not None:
        _ip.run_line_magic("rehashx", "")


def rerun_startup():
    """Rerun the files in the startup directory.

    Returns
    -------
    ret : dict
         Namespace of all successful files.

    """
    ret = {}
    for i in scandir('.'):
        if i.name.endswith('.py'):
            ret.update(runpy.run_path(i.name))
    return ret


if __name__ == "__main__":
    rehashx_run()
