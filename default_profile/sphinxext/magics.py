#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sphinx extension that allows us to properly use magics in the docs.

.. module:: magics

:URL: `<https://github.com/ipython/ipython/blob/master/docs/sphinxext/magics.py>`_

"""
import logging
import re
import sys

logging.basicConfig(format='%(name)-12s: %(levelname)-8s %(message)s')

try:
    from sphinx import addnodes
    # from sphinx.domains.std import StandardDomain
    from sphinx.roles import XRefRole
except (ImportError, ModuleNotFoundError) as e:
    logging.warning(e)
    # This has to be defined or else the module, and as a result,
    # the package come crashing down
    XRefRole = object

try:
    # Let's get a more useful error than raising exception
    from IPython.core.error import UsageError
except (ImportError, ModuleNotFoundError) as e:
    logging.warning(e)

    class UsageError(Exception):
        def __init__(self, err=None, *args, **kwargs):
            self.err = err
            super().__init__(self, *args, **kwargs)

        def __repr__(self):
            return '{}\t \t{}'.format(
                    self.__class__.__name__,
                    self.err)


        def __call__(self, err):
            """KEEP IT MOVIN' OVA THERE"""
            return self.__repr__(err)


name_re = re.compile(r"[\w_]+")


def parse_magic(env, sig, signode):
    """Extend Sphinx to handle IPython magics.

    Parameters
    ----------
    env : 

    Raises
    ------
    :exc:`IPython.core.error.UsageError`
        Raised when regular expression ``re.compile(r"[\w_]+")``
        doesn't match the signature of interest.

    """
    m = name_re.match(sig)
    if not m:
        raise UsageError("Invalid magic command: %s" % sig)
    name = "%" + sig
    signode += addnodes.desc_name(name, name)
    return m.group(0)


class LineMagicRole(XRefRole):
    """Cross reference role displayed with a % prefix."""
    prefix = "%"

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            title = self.prefix + title.lstrip("%")
        target = target.lstrip("%")
        return title, target


def parse_cell_magic(env, sig, signode):
    m = name_re.match(sig)
    if not m:
        raise ValueError("Invalid cell magic: %s" % sig)
    name = "%%" + sig
    signode += addnodes.desc_name(name, name)
    return m.group(0)


class CellMagicRole(LineMagicRole):
    """Cross reference role displayed with a %% prefix."""

    prefix = "%%"


def setup(app):
    app.add_object_type(
        'magic', 'magic', 'pair: %s; magic command', parse_magic
    )
    app.add_role_to_domain('std', 'linemagic', LineMagicRole(), override=True)

    app.add_object_type(
        'cellmagic', 'cellmagic', 'pair: %s; cell magic', parse_cell_magic
    )
    app.add_role_to_domain('std', 'cellmagic', CellMagicRole(), override=True)

    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True}
    return metadata
