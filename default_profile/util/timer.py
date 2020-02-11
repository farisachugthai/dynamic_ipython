#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===================================
Timer --- Create a timer decorator.
===================================

Largely this module was simply practice on writing decorators.

Might need to review logging best practices. I don't want the logger from
this module to emit anything, but it seems tedious to place that burden
on any module that imports from here.

.. seealso::

    :mod:`cProfile`
    :mod:`pstats`
    :mod:`timeit`
    :magic:`timeit`

"""
import functools
import logging
from os import scandir
from runpy import run_path
import time
from timeit import Timer

from IPython.core.getipython import get_ipython

logging.basicConfig(level=logging.INFO)


def timer(func):
    """Print the runtime of the decorated function.

    Utilizes `time.perf_counter`.

    .. todo:: Begin using the :mod:`timeit` module.

        There are more specialized ways of profiling things in
        other modules; however, this works for a rough estimate.

    Parameters
    ----------
    func : function
        Function to profile

    Returns
    -------
    value : float
        Output of function :func:`time.perf_counter()`.

    """
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
# I mean while we're practicing decorators throw this in the mix
def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]  # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)  # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")  # 4
        return value

    return wrapper_debug


def exc_timer(statement, setup=None):
    """A non-decorator implementation that uses `timeit.`"""
    t = Timer(stmt=statement, setup=setup)  # outside the try/except
    try:
        return t.timeit()
    except Exception:  # noqa E722
        t.print_exc()


class ArgReparser:
    """Class decorator that echoes out the arguments a function was called with."""
    def __init__(self, func):
        """Initialize the reparser with the function it wraps."""
        self.func = func

    def __call__(self, *args, **kwargs):
        print("entering function " + self.func.__name__)
        i = 0
        for arg in args:
            print("arg {0}: {1}".format(i, arg))
            i = i + 1

        return self.func(*args, **kwargs)


def time_dir(directory=None):
    if directory is None:
        directory = get_ipython().startup_dir
    result = []
    for i in scandir("."):
        if i.name.endswith(".py"):
            file = i.name
            print(file)
            print(time.time())
            start_time = time.time()
            exec(compile(open(file).read(), "timer", "exec"))
            end = time.time()
            diff = end - start_time
            print(f"{diff}")
            result.append((file, diff))

    return result
