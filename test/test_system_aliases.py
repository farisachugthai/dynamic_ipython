#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from IPython.testing.globalipapp import get_ipython
from default_profile.startup.system_aliases import validate_alias, Alias, CommonAliases


class TestAliases(unittest.TestCase):
    def setUp(self):
        self.shell = get_ipython()

    def test_initializing_my_alias(self):
        Alias("l", "ls -F --color=always")
