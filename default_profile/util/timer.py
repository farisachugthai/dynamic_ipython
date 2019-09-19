#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===================================
Timer --- Create a timer decorator.
===================================
.. module:: timer
    :synopsis: Create a decorator to time the execution time of modules.

.. highlight:: ipython

Largely this module was simply practice on writing decorators.

See Also
--------
:mod:`cProfile`
:mod:`pstats`
:mod:`timeit`
:magic:`timeit`

"""
import functools
import logging
import time

logging.basicConfig(level=logging.INFO)


def timer(func):
    """Print the runtime of the decorated function.

    Is this the right way to profile something on Windows btw?

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
