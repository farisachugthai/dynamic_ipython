#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

rehashx magic
-------------
This is an incredible little gem that's hugely useful for
making IPython work as a more versatile system shell.


Work in Progress
-----------------

The code that's more important than anything should execute regardless
of whether someone has ``pip install``-ed it.

In addition, enable faulthandler, tracemalloc and assign them to
sys.excepthook, threading.excepthoook and others.

A possible alternative to get_ipython().showsyntaxerror might possibly be
:func:`dis.distb`.

"""
import cgitb
import code
import faulthandler
import logging
import runpy
import sys
import threading
import trace
import traceback
from collections.abc import Sequence
from os import scandir
from pathlib import Path
from runpy import run_module, run_path
from traceback import FrameSummary, StackSummary
from tracemalloc import Snapshot

from IPython.core.getipython import get_ipython
from traitlets.config import Configurable


def rehashx_run():
    """Add all executables on the user's :envvar:`PATH` into the IPython ns.

    Parameters
    ----------
    shell : |ip| instance
        IPython shell instance.

    """
    get_ipython().run_line_magic("rehashx", "")


def get_exec_dir():
    _ip = get_ipython()
    if _ip is not None:
        exec_dir = _ip.profile_dir.startup_dir
    else:
        exec_dir = "."


def safe_run_path(fileobj, logger):
    logger.debug("File to execute is: %s", fileobj)
    try:
        return runpy.run_path(fileobj, init_globals=globals(), run_name="rerun_startup")
    except ImportError:
        logger.warning("ImportError for mod: ", sys.last_traceback)
    except ConnectionResetError:  # happens in windows async loop all the time
        pass
    except OSError as e:
        if hasattr(e, "winerror"):  # same reason
            pass
        else:
            logger.exception(e)
    except Exception as e:  # noqa
        logger.exception(e)
        raise
    except:
        traceback.print_exc()
        raise


def rerun_startup():
    """Rerun the files in the startup directory.

    Returns
    -------
    ret : dict
         Namespace of all successful files.

    """
    ret = {}
    exec_dir = get_exec_dir()
    logger = logging.getLogger(name=__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.WARNING)
    for i in scandir(exec_dir):
        if i.name.endswith(".py"):
            safe_run_path(i.name, logger=logger)
    return ret


def execfile(filename, global_namespace=None, local_namespace=None):
    """Python3 doesn't have this but it'd be nice to have a utility to exec a file at once."""
    if global_namespace is not dict:  # catch both None and any wrong formats
        global_namespace = globals()
    if local_namespace is not dict:  # catch both None and any wrong formats
        local_namespace = locals()
    with open(filename, "rb") as f:
        return exec(
            compile(f.read(), filename, "exec"), global_namespace, local_namespace
        )


def ipy_execfile(directory):
    for i in scandir(directory):
        get_ipython().run_line_magic("run", i.name)


class ExceptionHook(Configurable):
    """Custom exception hook for IPython."""

    instance = None

    def __init__(self, shell=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shell = shell

    def call(self, etype=None, evalue=None, etb=None):
        """Proxy for the call dunder."""
        if etype is None and evalue is None and etb is None:
            etype, evalue, etb = sys.exc_info()
        self.__call__(self, etype, evalue, etb)

    def __call__(self, etype, evalue, etb):
        """TODO."""
        pass

    def __repr__(self):
        return "<{} '{}'>".format(self.__class__.__name__, self.instance)


class ExceptionTuple(Sequence):
    """Simply a test for now but we need to provide the exception hook with this.

    It needs a tuple of exceptions to catch.

    Seemed like a good place to keep working with ABCs.
    """

    pass


if __name__ == "__main__":
    faulthandler.enable()
    _ip = get_ipython()

    if _ip is not None:
        rehashx_run()
        handled = cgitb.Hook(file=sys.stdout, format="text")
        sys.excepthook = handled
        _ip.excepthook = handled
