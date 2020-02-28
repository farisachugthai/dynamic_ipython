#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sphinx extension that allows us to properly use magics in the docs."""
from default_profile.startup import UsageError
import logging
import re

logging.basicConfig(format="%(name)-12s: %(levelname)-8s %(message)s")

try:
    from sphinx import addnodes

    # from sphinx.domains.std import StandardDomain
    from sphinx.roles import XRefRole
except (ImportError, ModuleNotFoundError) as e:
    logging.warning(e)
    # This has to be defined or else the module, and as a result,
    # the package come crashing down
    XRefRole = object


name_re = re.compile(r"[\w_]+")


def parse_magic(env, sig, signode):
    r"""Extend Sphinx to handle IPython magics.

    Parameters
    ----------
    env
        Genuinely unsure what any of these parameters are.

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
        """Generate a link without the leading :kbd:`%` in it."""
        if not has_explicit_title:
            title = self.prefix + title.lstrip("%")
        target = target.lstrip("%")
        return title, target


def parse_cell_magic(env, sig, signode):
    """Read rst documents and check for :kbd:`%%`."""
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
    app.add_object_type("magic", "magic", "pair: %s; magic command", parse_magic)
    app.add_role_to_domain("std", "linemagic", LineMagicRole(), override=True)

    app.add_object_type(
        "cellmagic", "cellmagic", "pair: %s; cell magic", parse_cell_magic
    )
    app.add_role_to_domain("std", "cellmagic", CellMagicRole(), override=True)

    metadata = {"parallel_read_safe": True, "parallel_write_safe": True}
    return metadata
