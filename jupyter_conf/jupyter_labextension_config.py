#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from traitlets.config import get_config
import logging
import os
import platform

logging.basicConfig()

# Configuration file for jupyter labextension.

c = get_config()


# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
c.Application.log_datefmt = "%Y-%m-%d %H:%M:%S"

# The Logging format template
c.Application.log_format = "[ %(created)f : %(name)s : %(highlevel)s : %(message)s : ]"

# Set the log level by value or name.
c.Application.log_level = 20


# ------------------------------------------------------------------------------
# JupyterApp(Application) configuration
# ------------------------------------------------------------------------------

# Base class for Jupyter applications

# Answer yes to any prompts.
# c.JupyterApp.answer_yes = False

# Full path of a config file.
# c.JupyterApp.config_file = ''

# Specify a config file to load.
# c.JupyterApp.config_file_name = ''

# Generate default config file.
# c.JupyterApp.generate_config = False

# ------------------------------------------------------------------------------
# LabExtensionApp(JupyterApp) configuration
# ------------------------------------------------------------------------------

# Base jupyter labextension command entry point

# JupyterLab Check
# Determine if we have a GUI since thatll be hugely necessary
if platform.platform().startswith('Linux'):
    user_env = os.environ.copy()
    try:
        user_env.get('DISPLAY')
    except AttributeError:
        pass

# Wait some of those were solid
c.CheckLabExtensionsApp.should_clean = True
