# Configuration file for jupyter contrib nbextension.
from traitlets.config import get_config

c = get_config()

# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
c.Application.log_datefmt = "%Y-%m-%d %H:%M:%S"

# The Logging format template
c.Application.log_format = "[ %(name)s  %(relativeCreated)d ] %(highlevel)s %(levelname)s %(module)s %(message)s "

# Set the log level by value or name.
c.Application.log_level = 30

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
# BaseContribNbextensionsApp(JupyterApp) configuration
# ------------------------------------------------------------------------------

# Base class for jupyter_contrib_nbextensions apps.

# ------------------------------------------------------------------------------
# JupyterContribApp(JupyterApp) configuration
# ------------------------------------------------------------------------------

# Root level jupyter_contrib app.

# Do these classes take any parameters?


# ------------------------------------------------------------------------------
# ContribNbextensionsApp(BaseContribNbextensionsApp) configuration
# ------------------------------------------------------------------------------

# Main jupyter_contrib_nbextensions application.
