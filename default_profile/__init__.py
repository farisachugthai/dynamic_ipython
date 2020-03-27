#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize the global IPython instance and begin configuring.

The heart of all IPython and console related code lives here.

Also a good check to see whats being counted as a package is::

>>> import pkg_resources
>>> for i in pkg_resources.find_distributions('.'):
...     print(i)
...
dynamic-ipython 0.0.2

>>> from setuptools import find_packages, find_namespace_packages
>>> found_packages = find_packages(where='.')
>>> found_namespace_packages = find_namespace_packages(where='.')
>>> logging.debug('Found packages were: {}'.format(found_packages))
>>> logging.debug('Found namespace packages were: {}'.format(found_namespace_packages))

"""
import importlib
import inspect
import logging
import os
import pkgutil
import sys
from collections import deque
from pathlib import Path
import __main__

import setuptools
import pkg_resources
from traitlets.config.application import LevelFormatter

try:
    __path__ = pkgutil.extend_path(__path__, os.path.dirname(os.path.abspath(__name__)))
    __path__.extend(setuptools.find_packages("."))
except NameError:
    pass

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

default_traitlets_log_format = "[ %(name)s  %(relativeCreated)d ] %(highlevel)s %(levelname)s %(module)s %(message)s "
default_formatter = LevelFormatter(fmt=default_traitlets_log_format)


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


class ModuleNotFoundError(ImportError):
    """Try to backport this for python3.6<."""

    __module__ = "builtins"  # for py3

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

    def __repr__(self):
        return "{}\n{}".format(self.__class__.__name__, self.__traceback__)


# Keep these imports below the ModuleNotFoundError backport
try:
    # these should always be available
    import IPython  # noqa F0401
    from IPython.core.getipython import get_ipython  # noqa F0401
except (ImportError, ModuleNotFoundError):
    pass

try:
    import __about__  # noqa
except:
    pass


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


QUEUE = deque(maxlen=1000)
FMT_NORMAL = logging.Formatter(
    fmt="%(asctime)s %(levelname).4s %(message)s", datefmt="%H:%M:%S"
)
FMT_DEBUG = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(levelname).4s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)


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
    root_logger = logging.getLogger()

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
        if logfile == "-":
            handlers.append(logging.StreamHandler())
        elif not Path(logfile).exists():
            handlers.append(logging.StreamHandler())
        else:
            handlers.append(logging.FileHandler(get_ipython().log_dir))

    for handler in handlers:
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        handler.addFilter(logging.Filter())
        root_logger.addHandler(handler)

    root_logger.setLevel(40)


# let me tell you i am LOVING this
try:
    from . import startup
except ImportError:
    importlib.invalidate_caches()
    print('startup not imported')
