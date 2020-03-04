#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the main startup for the IPython startup directory.

.. todo::

    So I think a good idea would be make this directory something that can be
    executed with 1 command, combine that and export it here.
    If something goes wrong in startup IPython doesn't finish executing the remaining files.
    So make it easy to re-exec.

"""
import asyncio
import platform
import sys
from asyncio.__main__ import AsyncIOInteractiveConsole, REPLThread
from asyncio import format_helpers
from os import scandir
from os.path import abspath

from pathlib import Path

try:
    from asyncio.windows_events import ProactorEventLoop, IocpProactor
except ImportError:
    # not available
    # from asyncio import ProactorEventLoop, IocpProactor
    pass

from prompt_toolkit.shortcuts import print_formatted_text as print
from IPython.core.getipython import get_ipython

# Are you allowed to do this? This shit confuses me so much
# Nope! Gotta figure out how relative imports and implicit imports work.
# from . import STARTUP_LOGGER


def exec_startup():
    """Be careful!!

    .. danger::
        All of the usual exec admonitions apply here.

    """
    exec(compile(open(__file__).read(), "<string>", "exec",), globals(), locals())


def exec_dir(directory):
    for i in scandir(directory):
        if i.name.endswith("py") or i.name.endswith("ipy"):
            exec(compile(open(i.name).read(), "<string>", "exec",), globals(), locals())


if "__name__" == "__main":
    shell = get_ipython()

    if not shell:
        print("startup.__main__: get_ipython returned None")

    this_dir = Path(__file__).parent
    # this doesn't do anything yet but hey at least we found the api
    if platform.platform().startswith("win"):
        proactor = IocpProactor()
        loop = ProactorEventLoop(proactor=proactor)
    else:

        loop = asyncio.new_event_loop()
    # breakpoint()

    repl_locals = {"asyncio": asyncio}
    for key in {
        "__name__",
        "__package__",
        "__loader__",
        "__spec__",
        "__builtins__",
        "__file__",
    }:
        repl_locals[key] = locals()[key]

    console = AsyncIOInteractiveConsole(repl_locals, loop)

    repl_future = None
    repl_future_interrupted = False

    repl_thread = REPLThread()
    repl_thread.daemon = True
    repl_thread.start()
    startup = abspath(".")
    exec_dir(startup)

    while True:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            if repl_future and not repl_future.done():
                repl_future.cancel()
                repl_future_interrupted = True
            continue
        except EOFError:
            sys.exit()
        except Exception as e:
            format_helpers.extract_stack(e)


