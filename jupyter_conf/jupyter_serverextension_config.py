"""Subcommand won't stop complaining about jupyterlab-git."""

# Configuration file for jupyter serverextension.

# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
# c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

# The Logging format template
# c.Application.log_format = '[%(name)s]%(highlevel)s %(message)s'

# Set the log level by value or name.
# c.Application.log_level = 30

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
# BaseExtensionApp(JupyterApp) configuration
# ------------------------------------------------------------------------------

# Base nbextension installer app

# Install from a Python package
# c.BaseExtensionApp.python = False

# Use the sys.prefix as the prefix
# c.BaseExtensionApp.sys_prefix = False

# Whether to do a user install
# c.BaseExtensionApp.user = False

# DEPRECATED: Verbosity level
# c.BaseExtensionApp.verbose = None

# ------------------------------------------------------------------------------
# ServerExtensionApp(BaseExtensionApp) configuration
# ------------------------------------------------------------------------------

# Root level server extension app
