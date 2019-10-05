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

See Also
--------
.. seealso::

    :mod:`cProfile`
    :mod:`pstats`
    :mod:`timeit`
    :magic:`timeit`

"""
import functools
import logging
import time
from timeit import Timer

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


def exc_timer(statement):
    """A non-decorator implementation that uses `timeit.`"""
    t = Timer(statement)  # outside the try/except
    try:
        t.timeit()
    # or t.repeat(...)
    except:  # noqa E722
        t.print_exc()
    # else:
    # TODO:
