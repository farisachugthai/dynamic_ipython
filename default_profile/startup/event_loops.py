"""
Asyncio operations
------------------

def extract_stack(f=None, limit=None):
    Replacement for traceback.extract_stack() that only does the
    necessary work for asyncio debug mode.

Well thats awesome.
"""
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

try:
    from trio import run
except:
    from asyncio import run

from asyncio.format_helpers import extract_stack
from asyncio.windows_events import ProactorEventLoop, IocpProactor

import logging
import multiprocessing
from multiprocessing.process import current_process

import platform

import threading


def children():
    """Simply to save the typing."""
    return multiprocessing.active_children()


def enable_multiprocessing_logging(level=30):
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(30)
    return logger


if __name__ == "__main__":
    if hasattr(asyncio.log.logger, "setLevel"):  # TODO: is this necessary?
        asyncio.log.logger.setLevel(logging.ERROR)

    # This doesn't do anything yet but hey at least we found the API
    if platform.platform().startswith("Win"):
        proactor = IocpProactor()
        loop = ProactorEventLoop(proactor=proactor)
