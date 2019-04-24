#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Easy Import --- Import commonly used modules into the IPython namespace.
========================================================================

This module is a slightly different way of importing things into the user's
interactive namespace.

Currently a module in this repository already exists and is launched on
startup.

As it stands, it may be preferable to use that over defining arbitrary
magic functions in ``extensions``.


"""
from IPython import get_ipython
from IPython.utils.importstring import import_item


def load_ns(mods):
    """Load modules into the namespace.

    Parameters
    ----------
    mods : module(s)
        Modules to import.

    Examples
    --------
    %ns mpl

    .. wait can you use an alias? i have a list `aliases down there but it's not initialized??
    """
    _ip = get_ipython()
    if not _ip.user_ns:
        _ip.user_ns = []
        # should probably check that this isn't empty after 20_aliases
        for mod in mods:
            if mod in aliases:
                _ip.user_ns.update(import_ns(namespaces[aliases[mod]]))


def load_ipython_extension(_ip):
    """Create ``ns`` magic."""
    _ip.magics_manager.register_function(load_ns, 'line', 'ns')
