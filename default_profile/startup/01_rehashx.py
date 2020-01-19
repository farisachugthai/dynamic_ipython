#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

rehashx magic
-------------

Run rehashx magic.

This is an incredible little gem that's hugely useful for
making IPython work as a more versatile system shell.

Work in Progress

-----------------
The code that's more important than anything should execute regardless
of whether someone has ``pip install``-ed it.


Exception Handling
------------------

Give a detailed, colored traceback and drop into pdb on exceptions.

This may have proved obvious to some but don't call
get_ipython().atexit_operations() during a terminal session you intend
on continuing....

So the IPython.core.ultratb mod was stated to be a port of cgitb.

Looks like we're in business!

Asyncio operations
------------------

def extract_stack(f=None, limit=None):
    Replacement for traceback.extract_stack() that only does the
    necessary work for asyncio debug mode.

Well thats awesome.

"""
import asyncio
import cgitb
import code
import faulthandler
import logging
import platform
import runpy
import sys
import trace
import traceback
from asyncio.events import (
    get_child_watcher,
    get_event_loop,
    get_event_loop_policy,
    get_running_loop,
)

try:
    from curio import Task
except:
    from asyncio.tasks import Task

from asyncio.tasks import current_task, all_tasks, create_task

try:
    from trio import run
except:
    from asyncio.events import run

from asyncio.format_helpers import extract_stack
from asyncio.windows_events import ProactorEventLoop, IocpProactor
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
        profiledir = Path(_ip.profile_dir)
        exec_dir = profiledir / "startup"
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
    _ip = get_ipython()

    faulthandler.enable()
    if hasattr(asyncio.log.logger, "setLevel"):  # TODO: is this necessary?
        asyncio.log.logger.setLevel(logging.ERROR)

    handled = cgitb.Hook(logdir=_ip.profile_dir.log_dir, file=sys.stdout, format="text")
    sys.excepthook = handled

    if _ip is not None:
        rehashx_run()
        _ip.excepthook = handled

    # This doesn't do anything yet but hey at least we found the API
    if platform.platform().startswith("Win"):
        proactor = IocpProactor()
        loop = ProactorEventLoop(proactor=proactor)

