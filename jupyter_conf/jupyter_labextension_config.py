#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jupyter Lab Extension Config.

.. currentmodule:: jupyterlab

.. highlight:: ipython

FYI

Subcommands
-----------

Subcommands are launched as `jupyter labextension cmd [args]`. For information
on using subcommand 'cmd', do: `jupyter labextension cmd -h`.

install
    Install labextension(s)
update
    Update labextension(s)
uninstall
    Uninstall labextension(s)
list
    List labextensions
link
    Link labextension(s)
unlink
    Unlink labextension(s)
enable
    Enable labextension(s)
disable
    Disable labextension(s)
check
    Check labextension(s)

"""
# Configuration file for jupyter labextension.
from traitlets.config import get_config
c = get_config()

import jupyter



# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

# The Logging format template
c.Application.log_format = '[ %(created)f : %(name)s : %(highlevel)s : %(message)s : ]'

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

#
# JupyterLab Check
#
class Foo(Bar):
    """

    $ jupyter labextension check --help-all

    Check labextension(s) by name

    Options
    -------
    --no-build
        Defer building the app after the action.
    --clean
        Cleanup intermediate files after the action.
    --installed
        Check only if the extension is installed.
    --app-dir=<Unicode> (BaseExtensionApp.app_dir)
        Default: ''
        The app directory to target
    --dev-build=<Bool> (BaseExtensionApp.dev_build)
        Default: True
        Whether to build in dev mode (defaults to dev mode)
    --debug-log-path=<Unicode> (DebugLogFileMixin.debug_log_path)
        Default: ''
        Path to use for the debug log file

    CheckLabExtensionsApp options
    -----------------------------
    --CheckLabExtensionsApp.answer_yes=<Bool>
        Default: False
        Answer yes to any prompts.
    --CheckLabExtensionsApp.app_dir=<Unicode>
        Default: ''
        The app directory to target
    --CheckLabExtensionsApp.config_file=<Unicode>
        Default: ''
        Full path of a config file.
    --CheckLabExtensionsApp.config_file_name=<Unicode>
        Default: ''
        Specify a config file to load.
    --CheckLabExtensionsApp.debug_log_path=<Unicode>
        Default: ''
        Path to use for the debug log file
    --CheckLabExtensionsApp.dev_build=<Bool>
        Default: True
        Whether to build in dev mode (defaults to dev mode)
    --CheckLabExtensionsApp.generate_config=<Bool>
        Default: False
        Generate default config file.
    --CheckLabExtensionsApp.log_datefmt=<Unicode>
        Default: '%Y-%m-%d %H:%M:%S'
        The date format used by logging formatters for %(asctime)s
    --CheckLabExtensionsApp.log_format=<Unicode>
        Default: '[%(name)s]%(highlevel)s %(message)s'
        The Logging format template
    --CheckLabExtensionsApp.log_level=<Enum>
        Default: 30
        Choices: (0, 10, 20, 30, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
        Set the log level by value or name.
    --CheckLabExtensionsApp.should_build=<Bool>
        Default: True
        Whether to build the app after the action
    --CheckLabExtensionsApp.should_check_installed_only=<Bool>
        Default: False
        Whether it should check only if the extensions is installed
    --CheckLabExtensionsApp.should_clean=<Bool>
        Default: False
        Whether temporary files should be cleaned up after building jupyterlab
    """
    pass

# Wait some of those were solid
c.CheckLabExtensionsApp.should_clean = True
