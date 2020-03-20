#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from traitlets.config.application import LevelFormatter

from default_profile.util.module_log import stream_logger

LOG_BASIC_FORMAT = "%(module)  %(created)f  [%(name)s]  %(highlevel)s  %(message)s  "

UTIL_LOGGER = logging.getLogger("default_profile").getChild("util")
UTIL_LOGGER.setLevel(logging.WARNING)
util_handler = logging.StreamHandler()
util_handler.setLevel(logging.WARNING)
util_handler.setFormatter(LevelFormatter(LOG_BASIC_FORMAT))
util_handler.addFilter(logging.Filter())
UTIL_LOGGER.addHandler(util_handler)
