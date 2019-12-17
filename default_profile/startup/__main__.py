#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the main startup for the IPython startup directory.

"""
import errno
import os
import sys

from IPython.core.getipython import get_ipython

global shell
shell = get_ipython()

if not shell:
    sys.exit('startup.__main__: get_ipython returned None')


def wrap_safe_execfile(executed):
    """Well I mean wrap it in a better way than bare Excepts."""
    try:
        shell.safe_execfile(executed)
    except ModuleNotFoundError as e:
        # TODO:
        return 'ModuleNotFoundError for {}'.format(e.__cause__)


# Why the hell would I ever do this
# for i in os.scandir():
#     wrap_safe_execfile(i.name)
