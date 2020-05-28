#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

The heart of all IPython and console related code lives here.

>>> import pkg_resources
>>> for i in pkg_resources.find_distributions('.'):
...     print(i)
...
dynamic-ipython 0.0.2

>>> from setuptools import find_packages, find_namespace_packages
>>> found_packages = find_packages(where='.')
>>> found_namespace_packages = find_namespace_packages(where='.')
>>> logging.debug('Found packages were: {}'.format(found_packages))

"""
import logging
import os
import sys
from collections import deque

# from packaging.version import Version

__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
]

__author__ = "Faris A. Chugthai"
__copyright__ = "Copyright 2018-2020 %s" % __author__
__email__ = "farischugthai@gmail.com"
__license__ = "MIT"
__package__ = "dynamic_ipython"
__summary__ = "Core utilities for Python packages"
__title__ = "dynamic_ipython"
__uri__ = "https://github.com/pypa/packaging"
# __version__ = Version("0.0.2")
__version__ = "0.0.2"


# Lol note that there are FOUR different logging.Formatter.fmt strings in this module
default_log_format = (
    "[ %(name)s  %(relativeCreated)d ] %(levelname)s %(module)s %(message)s "
)
PROFILE_DEFAULT_LOG = logging.getLogger(name="default_profile")
PROFILE_DEFAULT_LOG.setLevel(logging.WARNING)
PROFILE_DEFAULT_HANDLER = logging.StreamHandler()
PROFILE_DEFAULT_HANDLER.setLevel(logging.WARNING)

PROFILE_DEFAULT_FORMATTER = logging.Formatter(
    fmt=default_log_format, datefmt="%Y-%m-%d %H:%M:%S"
)

PROFILE_DEFAULT_HANDLER.addFilter(logging.Filterer())
PROFILE_DEFAULT_HANDLER.setFormatter(PROFILE_DEFAULT_FORMATTER)
PROFILE_DEFAULT_LOG.addHandler(PROFILE_DEFAULT_HANDLER)

QUEUE = deque(maxlen=1000)
FMT_NORMAL = logging.Formatter(
    fmt="%(asctime)s %(levelname).4s %(message)s", datefmt="%H:%M:%S"
)
FMT_DEBUG = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(levelname).4s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)


def ask_for_import(mod, package=None):
    """Import a module and return `None` if it's not found.

    Parameters
    ----------
    mod : str
        Module to import
    package : str, optional
        Package the module is found in.

    Returns
    -------
    imported : mod
        Module as imported by :func:`importlib.import_module`.

    """
    # Go for the low hanging fruit first
    import inspect
    import importlib
    if inspect.ismodule(mod):
        return importlib.import_module(mod, package=package)
    if inspect.getmodulename(mod):
        return importlib.import_module(inspect.getmodulename(mod), package=package)

    # Otherwise
    try:
        imported = importlib.import_module(mod, package=package)
    except (ImportError, ModuleNotFoundError):
        PROFILE_DEFAULT_LOG.warning("%s not imported", mod)
    except Exception:  # noqa
        if hasattr(sys, "last_type"):
            exception_name = sys.last_type
            PROFILE_DEFAULT_LOG.exception(exception_name)
    else:
        return imported


if sys.version_info < (3,7):
    class ModuleNotFoundError(ImportError):
        """Try to backport this for python3.6<."""

        __module__ = "builtins"  # for py3

        def __init__(self, *args, **kwargs):
            super().__init__(*args)

        def __repr__(self):
            return "{}\n{}".format(self.__class__.__name__, self.__traceback__)



# More logging stuff


class QueueHandler(logging.Handler):
    """This handler store logs events into a queue."""

    def __init__(self, queue, level=30):
        """Initialize an instance, using the passed queue."""
        self.queue = queue
        super().__init__(level=level)

    def enqueue(self, record):
        """Enqueue a log record."""
        self.queue.append(record)

    def emit(self, record):
        self.enqueue(self.format(record))



def setup_logging(debug=True, logfile=None):
    """
    All the produced logs using the standard logging function
    will be collected in a queue by the `queue_handler` as well
    as outputted on the standard error `stderr_handler`.

    The verbosity and the format of the log message is
    controlled by the `debug` parameter

    - debug=False:
        a concise log format will be used, debug messsages will be discarded
        and only important message will be passed to the `stderr_handler`

    - debug=True:
        an extended log format will be used, all messages will be processed
        by both the handlers
    """
    root_logger = logging.getLogger(name=__name__)

    if debug:
        log_level = logging.DEBUG
        formatter = FMT_DEBUG
    else:
        log_level = logging.INFO
        formatter = FMT_NORMAL

    handlers = [QueueHandler(QUEUE)]
    if not logfile:
        handlers.append(logging.StreamHandler())
    else:
        from pathlib import Path
        if logfile == "-":
            handlers.append(logging.StreamHandler())
        elif not Path(logfile).exists():
            handlers.append(logging.StreamHandler())
        else:

            # Keep these imports below the ModuleNotFoundError backport
            try:
                from IPython.core.getipython import get_ipython  # noqa F0401
            except (ImportError, ModuleNotFoundError):
                return

            handlers.append(logging.FileHandler(get_ipython().log_dir))

    for handler in handlers:
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        handler.addFilter(logging.Filter())
        root_logger.addHandler(handler)

    root_logger.setLevel(40)
    return root_logger

