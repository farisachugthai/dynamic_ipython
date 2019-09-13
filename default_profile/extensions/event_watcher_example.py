#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interactively watch a variable.

================
Event Watcher
================

.. module:: event_watcher_example
    :synopsis: Create an extension for IPython 7.0's new event handlers.

:URL: https://ipython.readthedocs.io/en/stable/config/callbacks.html#ipython-events

Provided by the IPython development team as an example of the new
input parser for release 7.0!!!

-----------------

IPython Events:
===============

Extension code can register callbacks functions which will be called on
specific events within the IPython code. You can see the current list of
available callbacks, and the parameters that will be passed with each, in the
callback prototype functions defined in IPython.core.events.
To register callbacks, use `IPython.core.events.EventManager.register().`

"""
from IPython import get_ipython


class VarWatcher:
    """Initialize an object that tracks different variables in the user namespace."""

    def __init__(self, ip=None, last_x=None):
        """Set :attr:`self.shell` to the global IPython instance and :attr:`self.last_x` to some var."""
        if ip is not None:
            self.shell = ip
        else:
            self.shell = get_ipython()
        self.last_x = last_x or None

    def pre_execute(self):
        self.last_x = self.shell.user_ns.get('x', None)

    def pre_run_cell(self, info):
        print('Cell code: "%s"' % info.raw_cell)

    def post_execute(self):
        if self.shell.user_ns.get('x', None) != self.last_x:
            print("x changed!")

    def post_run_cell(self, result):
        print('Cell code: "%s"' % result.info.raw_cell)
        if result.error_before_exec:
            print('Error before execution: %s' % result.error_before_exec)

    def load_ipython_extension(ip):
        vw = VarWatcher(ip)
        ip.events.register('pre_execute', vw.pre_execute)
        ip.events.register('pre_run_cell', vw.pre_run_cell)
        ip.events.register('post_execute', vw.post_execute)
        ip.events.register('post_run_cell', vw.post_run_cell)
