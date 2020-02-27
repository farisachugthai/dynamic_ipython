#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
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

# messes up %run
try:
    from trio import run as _async_run
except:
    from asyncio import run as _async_run

import logging
import multiprocessing
from multiprocessing.process import current_process
import platform
import shlex
import threading

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

        In [40]: await system_command('ls')

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
    if len(asyncio.log.logger.root.handlers) > 0:
        asyncio.log.logger.root.handlers.pop()
    asyncio.log.logger.setLevel(99)
    asyncio.log.logger.root.setLevel(99)
    enable_multiprocessing_logging()
