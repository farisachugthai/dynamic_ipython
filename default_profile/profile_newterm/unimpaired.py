#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Todo:

(dynamic_ipython) 19:00:17 u0_a144@localhost Wed Nov 27 ~/projects/dynamic_ipython/default_profile

$: ipython --profile=newterm
[TerminalIPythonApp] WARNING | Error in loading extension: storemagic
Check your config files in /data/data/com.termux/files/home/projects/dynamic_ipython/default_profile/profile_newterm
Traceback (most recent call last):
  File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/shellapp.py", line 261, in init_extensions
    self.shell.extension_manager.load_extension(ext)
  File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/extensions.py", line 87, in load_extension
    if self._call_load_ipython_extension(mod):
  File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/extensions.py", line 134, in _call_load_ipython_extension
    mod.load_ipython_extension(self.shell)
  File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/extensions/storemagic.py", line 225, in load_ipython_extension
    ip.register_magics(StoreMagics)
  File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/magic.py", line 405, in register
    m = m(shell=self.shell)
  File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/extensions/storemagic.py", line 69, in __init__
    super(StoreMagics, self).__init__(shell=shell)
  File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/magic.py", line 535, in __init__
    tab[magic_name] = getattr(self, meth_name)
AttributeError: 'StoreMagics' object has no attribute 'load_ext'

"""
import logging
import os
from reprlib import Repr
import sys

logging.basicConfig(level = logging.INFO)

import traitlets
from traitlets.config.loader import Config

from IPython import get_ipython
from IPython.core.magics.basic import BasicMagics
from IPython.extensions.storemagic import StoreMagics
from IPython.terminal.interactiveshell import TerminalInteractiveShell


class TerminallyUnimpaired(TerminalInteractiveShell):
    """What do we need to implement?

    Assuming this'll crash then we can notate what was required.

    We crashed on loading magics? Weird.
    Uhh I'm just gonna add a Config to ensure that it's there.

    """
    def __repr__(self):
        truncated = Repr().repr(self.__class__.__name__)
        return ''.format(truncated)

    def begin(self):
        """The superclass already defined initialize, initlialized, init_* and start.

        So let's go with begin.
        """
        super().initialize()
        if self.config is None:
            self.config = Config()


# StoreMagics(get_ipython()).unobserve_all()
