#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from reprlib import Repr
import sys

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


StoreMagics(get_ipython()).unobserve_all()
