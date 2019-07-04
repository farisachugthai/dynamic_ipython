#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a timer decorator."""
import functools
import logging
import time

logging.basicConfig(level=logging.INFO)


def timer(func):
    """Print the runtime of the decorated function. Is this the right way to profile something on Windows btw?"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logging.info(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer

# class ModuleTimer()
