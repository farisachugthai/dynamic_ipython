#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========
`%rehashx`
==========

This is an incredible little gem that's hugely useful for
making IPython work as a more versatile system shell.

For the future we should consider moving all imports from this package out and
keeping only "*Mission Critical*" type code in the first file.

The code that's more important than anything should execute regardless
of whether someone has ``pip install``-ed it.

"""
from IPython import get_ipython


def main():
    """Add all executables on the user's :envvar:`PATH` into the IPython ns.

    Now Im wondering if it would be easier to do this after setting up the aliases.

    Parameters
    ----------
    shell : |ip| instance
        IPython shell instance.

    """
    _ip = get_ipython()
    if _ip is not None:
        _ip.run_line_magic('rehashx', '')


if __name__ == "__main__":
    main()
