#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Jupyter Lab Extension Config.

-----

.. module:: jupyter_labextension_config

"""
# Configuration file for jupyter labextension.
from traitlets.config import get_config
c = get_config()

# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

# The Logging format template
c.Application.log_format = '[%(name)s]%(highlevel)s %(message)s'

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