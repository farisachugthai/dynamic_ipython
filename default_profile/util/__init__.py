#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains a collection of utility scripts.

==========
Utilities
==========

The modules contained in this package are, generally speaking, a collection of
scripts that I've found useful while working with IPython, but that unfortunately
haven't been fleshed out enough.

They're still all useful in their current state and when the user is
running IPython interactively, but none of the scripts havet been fleshed out
to the extent that they could be easily changed to IPython extensions.

Currently the module aims to:

#) Create consistent `logging.Logger` objects
#) Make a better pager on Windows
#) Create a collection of classes that can more easily remove
   platform-specific issues that continue to arise.

In addition, configure a module-wide logger by equating `logging.BASIC_FORMAT`
with a pre-determined template string like so::

    >>> logging.BASIC_FORMAT = '%(asctime)s : %(levelname)s : %(message)s'
    >>> UTIL_LOGGER = logging.getLogger('default_profile.util')
    >>> UTIL_LOGGER.setLevel(logging.WARNING)

Pandas
------

In addition, 2 classes have been taken verbatim from the Pandas dev team.
The classes are used to create :keyword:`dict` style objects that also
allow for attribute-style access.

"""
import logging
import os
import sys
from logging import NullHandler

from . import module_log, machine, timer

logging.BASIC_FORMAT = '%(created)f : %(module)s : %(levelname)s : %(message)s'

UTIL_LOGGER = logging.getLogger('default_profile').getChild('util')
UTIL_LOGGER.setLevel(logging.WARNING)


class DictWrapper(object):
    """ provide attribute-style access to a nested dict"""

    def __init__(self, d, prefix=""):
        object.__setattr__(self, "d", d)
        object.__setattr__(self, "prefix", prefix)

    def __setattr__(self, key, val):
        prefix = object.__getattribute__(self, "prefix")
        if prefix:
            prefix += "."
        prefix += key
        # you can't set new keys
        # can you can't overwrite subtrees
        if key in self.d and not isinstance(self.d[key], dict):
            _set_option(prefix, val)
        else:
            raise OptionError("You can only set the value of existing options")

    def __getattr__(self, key):
        prefix = object.__getattribute__(self, "prefix")
        if prefix:
            prefix += "."
        prefix += key
        try:
            v = object.__getattribute__(self, "d")[key]
        except KeyError:
            raise OptionError("No such option")
        if isinstance(v, dict):
            return DictWrapper(v, prefix)
        else:
            return _get_option(prefix)

    def __dir__(self):
        return list(self.d.keys())

# For user convenience,  we'd like to have the available options described
# in the docstring. For dev convenience we'd like to generate the docstrings
# dynamically instead of maintaining them by hand. To this, we use the
# class below which wraps functions inside a callable, and converts
# __doc__ into a property function. The doctsrings below are templates
# using the py2.6+ advanced formatting syntax to plug in a concise list
# of options, and option descriptions.


class CallableDynamicDoc(object):

    def __init__(self, func, doc_tmpl):
        self.__doc_tmpl__ = doc_tmpl
        self.__func__ = func

    def __call__(self, *args, **kwds):
        return self.__func__(*args, **kwds)

    @property
    def __doc__(self):
        opts_desc = _describe_option('all', _print_desc=False)
        opts_list = pp_options_list(list(_registered_options.keys()))
        return self.__doc_tmpl__.format(opts_desc=opts_desc,
                                        opts_list=opts_list)
