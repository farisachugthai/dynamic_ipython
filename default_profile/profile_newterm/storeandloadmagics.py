#!/usr/bin/env python
# -*- coding: utf-8 -*-
from IPython.core.getipython import get_ipython
from IPython.extensions.storemagic import StoreMagics


# StoreMagics(get_ipython()).unobserve_all()
class StoreAndLoadMagics(StoreMagics):
    """I keep getting an error about this."""

    def __init__(self, shell=None, *args, **kwargs):
        """TODO: Docstring for function."""
        super().__init__(self, *args, **kwargs)
        self.shell = shell or get_ipython()

    def load_ext(self):
        self.shell.register_magics(self)

    # Load the extension in IPython.
    def register_magic(self, ip):
        """Are you allowed to do this?"""
        ip.register_magics(self)


def load_ipython_extension(ip=None):
    """Load the extension in IPython."""
    if ip is None:
        ip = get_ipython()

    storemagic = StoreMagics(ip)
    ip.register_magics(storemagic)
    # ip.events.register('pre_run_cell', storemagic.pre_run_cell)
    # ip.events.register('post_execute', storemagic.post_execute_hook)
