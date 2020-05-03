#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

LOG_BASIC_FORMAT = "%(module)  %(created)f  [%(name)s]  %(highlevel)s  %(message)s  "

UTIL_LOGGER = logging.getLogger("default_profile").getChild("util")
UTIL_LOGGER.setLevel(logging.WARNING)
util_handler = logging.StreamHandler()
util_handler.setLevel(logging.WARNING)
util_handler.setFormatter(logging.Formatter(LOG_BASIC_FORMAT))
util_handler.addFilter(logging.Filter(name=__name__))
UTIL_LOGGER.addHandler(util_handler)
