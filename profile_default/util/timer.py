#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a timer decorator.

======
Timer
======

.. module:: timer

.. highlight:: ipython

Largely this module was simply practice on writing decorators.

.. todo::

    Explore the module :mod:`timeit()` or IPython's ``%timeit`` magic.

See Also
--------
:mod:`profile_default.01_rehashx` : module
    Module where :ref:`profile_default.01_rehashx.main` is wrapped with the
    timer decorator.

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
