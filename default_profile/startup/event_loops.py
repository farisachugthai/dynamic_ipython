#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from asyncio.events import get_event_loop_policy

try:
    # get_event_loop() is one of the most frequently called
    # functions in asyncio.  Pure Python implementation is
    # about 4 times slower than C-accelerated.
    from _asyncio import (
        _get_running_loop,
        _set_running_loop,
        get_running_loop,
        get_event_loop,
    )
except ImportError:
    from asyncio.events import (
        _get_running_loop,
        _set_running_loop,
        get_running_loop,
        get_event_loop,
    )

import logging
import multiprocessing

# from multiprocessing.process import current_process
import platform
import shlex
import threading

# from threading and _threading_local
import sys as _sys

try:
    from _thread import _local as local
    from _thread import _excepthook as excepthook, _ExceptHookArgs as ExceptHookArgs
except ImportError:
    # Simple Python implementation if _thread._excepthook() is not available
    from traceback import print_exception as _print_exception
    from collections import namedtuple
    from _threading_local import local

    _ExceptHookArgs = namedtuple(
        "ExceptHookArgs", "exc_type exc_value exc_traceback thread"
    )

    def ExceptHookArgs(args):
        """Return a namedtuple of 'exc_type exc_value exc_traceback thread'."""
        return _ExceptHookArgs(*args)

    def excepthook(args, /):
        """Handle uncaught `threading.Thread.run` exception."""
        if args.exc_type == SystemExit:
            # silently ignore SystemExit
            return

        if _sys is not None and _sys.stderr is not None:
            stderr = _sys.stderr
        elif args.thread is not None:
            stderr = args.thread._stderr
            if stderr is None:
                # do nothing if sys.stderr is None and sys.stderr was None
                # when the thread was created
                return
        else:
            # do nothing if sys.stderr is None and args.thread is None
            return

        if args.thread is not None:
            name = args.thread.name
        else:
            name = threading.get_ident()
        print(f"Exception in thread {name}:", file=stderr, flush=True)
        _print_exception(args.exc_type, args.exc_value, args.exc_traceback, file=stderr)
        stderr.flush()


# try:
#     from curio import Task
# except:
#     from asyncio.tasks import Task

from curio import Kernel
from curio.debug import logcrash, longblock

# from asyncio.tasks import current_task, all_tasks, create_task

# messes up %run
# try:
#     from trio import run as _async_run
# except:
#     from asyncio import run as _async_run
from IPython.core.getipython import get_ipython


def children():
    """Return `multiprocessing.active_children`. Simply to save the typing."""
    return multiprocessing.active_children()


def enable_multiprocessing_logging(level=50):
    """Log to stderr."""
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(level)
    return logger


async def system_command(command_to_run):
    """Run a system command using prompt_toolkit's run_system_command.

    Examples
    --------
    ::

        In [40]: await system_command('ls')  # +NORMALIZE_WHITESPACE
        01_rehashx.py       20_aliases.py        31_yank_last_arg.py
        36_ptutils.py     cscope.out  05_log.py           21_fzf.py
        32_kb.py              41_numpy_init.py  event_loops.py 06_help_helpers.py
        22_alias_manager.py  33_bottom_toolbar.py  43_matplotlib.py
        interpreter.py 10_envvar.py        23_git_commands.py   34_completion.py
        __init__.py       repralias.py
        11_clipboard.py     30_readline.py       35_lexer.py
        __main__.py       tags

    Whoo!
    """
    if hasattr(command_to_run, "startswith"):
        com = shlex.quote(command_to_run)
        command_to_run = shlex.split(com)
    else:
        if not hasattr(command_to_run, "append"):
            raise TypeError

    await get_ipython().pt_app.app.run_system_command(
        command=com, wait_for_enter=False, wait_text="", display_before_text=""
    )


def initialize_kernel():
    """Initialize a `curio.Kernel`."""
    return Kernel([longblock, logcrash])


async def kernel_run(command, kernel):
    return await kernel.run(
        subprocess.run(
            shlex.split(shlex.quote(command)),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    )


async def subproc(command):
    results = []
    try:
        async with timeout_after(0.5):
            # TODO: might want to preprocess the command
            out = await subprocess.run(
                [command], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
    except TaskTimeout as e:
        results.append("timeout")
        results.append(e.stdout)
        results.append(e.stderr)
    return results


if __name__ == "__main__":
    # Me trying to shut the loggers up
    if len(asyncio.log.logger.root.handlers) > 0:
        asyncio.log.logger.root.handlers.pop()
    if len(asyncio.log.logger.handlers) > 0:
        asyncio.log.logger.handlers.pop()

    asyncio.log.logger.setLevel(99)
    asyncio.log.logger.root.setLevel(99)
    if len(logging.root.handlers) > 0:
        logging.root.handlers.pop()
    logging.root.setLevel(99)
    asyncio.log.logger.disabled = True
    asyncio.log.logger.root.disabled = True

    event_policy = get_event_loop_policy()
    try:
        loop = get_running_loop()
    except RuntimeError:
        # sigh
        loop = event_policy.new_event_loop()

    if not platform.platform().startswith("Win"):
        # This raises a NotImplementedError on Windows
        watcher = event_policy.get_child_watcher()
