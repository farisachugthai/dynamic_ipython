#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==================================================
IPython --- Configuration file for :mod:`IPython`.
==================================================

Notes
-----
.. note::

    The standard :func:`IPython.get_ipython` function returns `None`
    so I suppose IPython hasn't officially instantiated yet.

.. code-block:: ipython

    from IPython import get_ipython
    _ip = get_ipython()

Therefore that function shouldn't be used anywhere in this file.

"""
import builtins
import logging
import os
import platform
import shutil
import sys
import traceback
from pathlib import Path

from IPython.core.release import version_info

# THIS IS THE MODULE! Its too exciting to able to execute this script
# directly from within python and not get an error for a func call with no
# import
from traitlets.config import get_config, Configurable

logging.basicConfig(level=logging.INFO, format=logging.BASIC_FORMAT)
c = get_config()


try:
    from unimpaired import TerminallyUnimpaired
except:  # noqa
    pass


def get_home():
    """Define the user's :envvar:`HOME`."""
    try:
        home = Path.home()
    except OSError:
        home = os.environ.get("%userprofile%")
    return home


home = get_home()

if ModuleNotFoundError not in dir(builtins):

    from default_profile import ModuleNotFoundError
c.InteractiveShellApp.reraise_ipython_extension_failures = False

c.Application.log_datefmt = "%Y-%m-%d %H:%M:%S"

c.Application.log_format = (
    "%(module) : %(created)f : [%(name)s] : %(highlevel)s : %(message)s : "
)

# Set the log level by value or name.
c.Application.log_level = 30

# variable IPYTHONDIR.
if os.environ.get("IPYTHONDIR"):
    c.BaseIPythonApplication.ipython_dir = os.environ.get("IPYTHONDIR")
else:
    # Assume home was defined correctly up top. Will need to rewrite for windows
    c.BaseIPythonApplication.ipython_dir = os.path.join(home, ".ipython")

# Whether to overwrite existing config files when copying
# c.BaseIPythonApplication.overwrite = False

# The IPython profile to use.
c.BaseIPythonApplication.profile = "newterm"

# Create a massive crash report when IPython encounters what may be an internal
#  error.  The default is to append a short message to the usual traceback
c.BaseIPythonApplication.verbose_crash = False

# ----------------------------------------------------------------------------
# TerminalIPythonApp(BaseIPythonApplication,InteractiveShellApp) configuration
# ----------------------------------------------------------------------------

# Whether to display a banner upon starting IPython.
c.TerminalIPythonApp.display_banner = False

# If a command or file is given via the command-line, e.g. 'ipython foo.py',
#  start an interactive shell after executing the file or command.
c.TerminalIPythonApp.force_interact = True

# Dec 08, 2019: Adding this in
c.TerminalIPythonApp.log_format = (
    "%(module) : %(created)f : [%(name)s] : %(highlevel)s : %(message)s : "
)

# An enhanced, interactive shell for Python.

# 'all', 'last', 'last_expr' or 'none', 'last_expr_or_assign' specifying which
#  nodes should be run interactively (displaying output from expressions).
c.InteractiveShell.ast_node_interactivity = "last_expr_or_assign"

# AKA:  Make IPython automatically call any callable object even if you didn't type

# A list of ast.NodeTransformer subclass instances, which will be applied to
#  user input before code is run.
# c.InteractiveShell.ast_transformers = []

c.InteractiveShell.autoawait = False

c.InteractiveShell.autocall = 0

c.InteractiveShell.banner1 = ""

c.InteractiveShell.banner2 = ""
c.InteractiveShell.cache_size = 10000
c.InteractiveShell.color_info = True
c.InteractiveShell.colors = "Linux"

c.InteractiveShell.debug = True


if platform.system() == "Windows":
    c.InteractiveShell.display_page = True
else:
    if shutil.which("bat"):
        c.InteractiveShell.display_page = False

c.InteractiveShell.history_length = 50000

c.InteractiveShell.history_load_length = 10000
c.InteractiveShell.pdb = True

c.InteractiveShell.quiet = False
c.InteractiveShell.wildcards_case_sensitive = False
c.InteractiveShell.xmode = "Verbose"

# Autoformatter to reformat Terminal code. Can be `'black'` or `None`
if shutil.which("black"):
    c.TerminalInteractiveShell.autoformatter = "black"
else:
    c.TerminalInteractiveShell.autoformatter = None

c.TerminalInteractiveShell.confirm_exit = False

# Options for displaying tab completions, 'column', 'multicolumn', and
#  'readlinelike'. These options are for `prompt_toolkit`, see `prompt_toolkit`
#  documentation for more information.
c.TerminalInteractiveShell.display_completions = "readlinelike"

# Shortcut style to use at the prompt. 'vi' or 'emacs'.
# Ah I forgot <C-a> on Tmux and Emacs clobber.

# Well windows doesn't get tmux so.

if platform.system() == "Windows":
    c.TerminalInteractiveShell.editing_mode = "emacs"
else:
    if os.environ.get("TMUX"):
        c.TerminalInteractiveShell.editing_mode = "vi"
        # I don't know if this is the right way to do this
        c.TerminalInteractiveShell.prompt_includes_vi_mode = False
# c.TerminalInteractiveShell.display_completions = 'column'
c.TerminalInteractiveShell.display_completions = "readlinelike"

c.TerminalInteractiveShell.editing_mode = "emacs"

# TODO:
# c_logger.info("Editing Mode:\t {!s}", c.TerminalInteractiveShell.editing_mode)

# Set the editor used by IPython (default to $EDITOR/vi/notepad).
c.TerminalInteractiveShell.editor = "nvim"

# Allows to enable/disable the prompt toolkit history search
# c.TerminalInteractiveShell.enable_history_search = True

# Enable vi (v) or Emacs (C-X C-E) shortcuts to open an external editor.
# This is in addition to the F2 binding, which is always enabled.
c.TerminalInteractiveShell.extra_open_editor_shortcuts = True


def get_env():
    """Would it make sense to combine functools.lru_cache with this?"""
    return os.environ.copy()


c.TerminalInteractiveShell.space_for_menu = 0

# Automatically set the terminal title
c.TerminalInteractiveShell.term_title = True

# Customize the terminal title format.  This is a python format string.
# Available substitutions are: {cwd}.
c.TerminalInteractiveShell.term_title_format = "IPython: {cwd}"

# Use 24bit colors instead of 256 colors in prompt highlighting. If your
# terminal supports true color, the following command should print 'TRUECOLOR'
# in orange: printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"
c.TerminalInteractiveShell.true_color = True


# Switch modes for the IPython exception handlers.
# Default: 'Context'
# Choices: ['Context', 'Plain', 'Verbose', 'Minimal']
c.TerminalInteractiveShell.xmode = "Minimal"

# ----------------------------------------------------------------------------
# HistoryAccessor(HistoryAccessorBase) configuration
# ----------------------------------------------------------------------------

# Access the history database without adding to it.

# This is intended for use by standalone history tools. IPython shells use
# HistoryManager, below, which is a subclass of this.

# Values of 1 or less effectively disable caching.
c.HistoryManager.db_cache_size = 16

# Should the history database include output? (default: no)
c.HistoryManager.db_log_output = True

# Enable debug for the Completer. Mostly print extra information for
#  experimental jedi integration.
c.Completer.debug = False

c.Completer.jedi_compute_type_timeout = 0

c.Completer.use_jedi = False

c.IPCompleter.omit__names = 1
