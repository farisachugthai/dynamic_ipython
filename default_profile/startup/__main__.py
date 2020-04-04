#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the main startup for the IPython startup directory."""
import asyncio
import platform
import sys

try:
    from asyncio.__main__ import AsyncIOInteractiveConsole, REPLThread
except ImportError:  # py3.8 only
    AsyncIOInteractiveConsole = REPLThread = None

from asyncio import format_helpers
from os import scandir
from os.path import abspath
from pathlib import Path
from pprint import pprint as print

try:
    from asyncio.windows_events import ProactorEventLoop, IocpProactor
except ImportError:
    # not available
    # from asyncio import ProactorEventLoop, IocpProactor
    pass

from IPython.core.getipython import get_ipython


def exec_startup():
    """Runs `exec(compile(__file__))`.

    .. danger::
        All of the usual exec admonitions apply here.

    """
    exec(compile(open(__file__).read(), "<string>", "exec",), globals(), locals())


def exec_dir(directory):
    for i in scandir(directory):
        if i.name.endswith("py") or i.name.endswith("ipy"):
            exec(compile(open(i.name).read(), "<string>", "exec",), globals(), locals())


def async_startup():
    """An interactive console with asyncio.

    Initializes an asyncio event loop and the standard libraries
    AsyncIOInteractiveConsole.
    """
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

    console = AsyncIOInteractiveConsole

    repl_future = None
    repl_future_interrupted = False

    repl_thread = REPLThread
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
                print("Interrupted!")
        except EOFError:
            sys.exit()
            # better than raise?
        except Exception as e:
            print(format_helpers.extract_stack(e))


if "__name__" == "__main__":
    async_startup()
