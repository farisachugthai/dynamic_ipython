#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

from asyncio.events import (
    #     get_child_watcher,
    #     get_event_loop,
    get_event_loop_policy,
    get_running_loop,
)
import multiprocessing

# from multiprocessing.process import current_process
import platform
import shlex

# from threading
try:
    from _thread import _excepthook as excepthook, _ExceptHookArgs as ExceptHookArgs
except ImportError:
    # Simple Python implementation if _thread._excepthook() is not available
    from traceback import print_exception as _print_exception
    from collections import namedtuple

    _ExceptHookArgs = namedtuple(
        "ExceptHookArgs", "exc_type exc_value exc_traceback thread"
    )

    def ExceptHookArgs(args):
        return _ExceptHookArgs(*args)

    def excepthook(args, /):
        """
        Handle uncaught Thread.run() exception.
        """
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
            name = get_ident()
        print(f"Exception in thread {name}:", file=stderr, flush=True)
        _print_exception(args.exc_type, args.exc_value, args.exc_traceback, file=stderr)
        stderr.flush()


# try:
#     from curio import Task
# except:
#     from asyncio.tasks import Task

# from asyncio.tasks import current_task, all_tasks, create_task

# messes up %run
# try:
#     from trio import run as _async_run
# except:
#     from asyncio import run as _async_run
from IPython.core.getipython import get_ipython


def children():
    """Simply to save the typing."""
    return multiprocessing.active_children()


def enable_multiprocessing_logging(level=30):
    """Log to stderr."""
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(30)
    return logger


async def system_command(command_to_run):
    """Run a system command.

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


if __name__ == "__main__":
    try:
        loop = get_running_loop()
    except RuntimeError:
        # sigh
        event_policy = get_event_loop_policy()
        loop = event_policy.new_event_loop()
