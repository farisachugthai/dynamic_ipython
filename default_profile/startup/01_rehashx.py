#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run rehashx magic.

This is an incredible little gem that's hugely useful for
making IPython work as a more versatile system shell.

The code that's more important than anything should execute regardless
of whether someone has ``pip install``-ed it.

Give a detailed, colored traceback and drop into pdb on exceptions.

This may have proved obvious to some but don't call
get_ipython().atexit_operations() during a terminal session you intend
on continuing....

So the IPython.core.ultratb mod was stated to be a port of cgitb.

Looks like we're in business!

"""
import asyncio
import cgitb
import code
import faulthandler
import logging
import runpy
import sys
import trace
import traceback
from asyncio.events import (get_child_watcher, get_event_loop,
                            get_event_loop_policy, get_running_loop)
from asyncio.tasks import Task
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
        exec_dir = profile_dir / "startup"
    else:
        exec_dir = "."


def rerun_startup(logger=None):
    """Rerun the files in the startup directory.

    Returns
    -------
    ret : dict
         Namespace of all successful files.

    """
    curdir = Path.cwd().resolve()
    if logger is None:
        logger = logging.getLogger(name=__name__)
        logger.addHandler(logging.StreamHandler())
    logger.debug("Curdir. %s", curdir)
    ret = {}
    exec_dir = get_exec_dir()
    for i in scandir(exec_dir):
        if i.name.endswith(".py"):
            try:
                ret.update(
                    runpy.run_path(
                        i.name, init_globals=globals(), run_name="rerun_startup"
                    )
                )
            except ImportError:
                print("ImportError for mod: ", sys.last_traceback)
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
    if _ip is not None:
        rehashx_run()
        handled = cgitb.Hook(
            logdir=_ip.profile_dir.log_dir, file=sys.stdout, format="text"
        )
        sys.excepthook = handled
        # supposed to be used on the class not the instance
        # _ip.add_traits({"interpreter": code.InteractiveConsole(locals())})
        _ip.write = handled
        _ip.interpreter = code.InteractiveConsole()
        # _ip.showsyntaxerror = _ip.interpreter.showsyntaxerror
        # _ip.showtraceback = _ip.interpreter.showtraceback
