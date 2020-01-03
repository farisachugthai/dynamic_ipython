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

from IPython.terminal.prompts import ClassicPrompts
from IPython.core.release import version_info

# THIS IS THE MODULE! Its too exciting to able to execute this script
# directly from within python and not get an error for a func call with no
# import
from traitlets.config import get_config, Configurable

default_log_format = (
    "[ %(name)s  %(relativeCreated)d ] %(levelname)s %(module)s %(message)s "
)

logging.basicConfig(level=logging.INFO, format=default_log_format)

c = get_config()
# admonition: Don't it this way
# c = Configurable()

try:
    import default_profile
except (ImportError, ModuleNotFoundError):
    default_profile = None
    logging.error("import error for default_profile")
    # todo: realistically we should also set exec_files to None since everything ./startup is gonna crash
else:
    from default_profile import PROFILE_DEFAULT_LOG

    import __main__
    # 3.6 compat
    if ModuleNotFoundError not in dir(builtins):
        from default_profile import ModuleNotFoundError


def get_home():
    """Define the user's :envvar:`HOME`."""
    try:
        home = Path.home()
    except OSError:
        home = os.environ.get("%userprofile%")
    return home


home = get_home()


# ----------------------------------------------------------------------------
# InteractiveShellApp(Configurable) configuration
# ----------------------------------------------------------------------------

# A Mixin for applications that start InteractiveShell instances.
#
#  Provides configurables for loading extensions and executing files as part of
#  configuring a Shell environment.
#
#  The following methods should be called by the :meth:`initialize` method of
#  the subclass:
#
#    - :meth:`init_path`
#    - :meth:`init_shell` (to be implemented by the subclass)
#    - :meth:`init_gui_pylab`
#    - :meth:`init_extensions`
#    - :meth:`init_code`

# Execute the given command string.
# c.InteractiveShellApp.code_to_run = ''

# Run the file referenced by the PYTHONSTARTUP environment variable at IPython
# startup.
# c.InteractiveShellApp.exec_PYTHONSTARTUP = True

# List of files to run at IPython startup.
# c.InteractiveShellApp.exec_files = []

# lines of code to run at IPython startup.
# c.InteractiveShellApp.exec_lines = []

# A list of dotted module names of IPython extensions to load.

# dotted module name of an IPython extension to load.
# c.InteractiveShellApp.extra_extension = ''

# A file to be run
# c.InteractiveShellApp.file_to_run = ''

# Enable GUI event loop integration with any of ('asyncio', 'glut', 'gtk',
#  'gtk2', 'gtk3', 'osx', 'pyglet', 'qt', 'qt4', 'qt5', 'tk', 'wx', 'gtk2',
#  'qt4').
# c.InteractiveShellApp.gui = None

# Should variables loaded at startup (by startup files, exec_lines, etc.) be
# hidden from tools like %who?
# c.InteractiveShellApp.hide_initial_ns = True

# Configure matplotlib for interactive use with the default matplotlib backend.

#     Default: None
#     Choices: ['auto', 'agg', 'gtk', 'gtk3', 'inline', 'ipympl', 'nbagg',
#     notebook', 'osx', 'pdf', 'ps', 'qt', 'qt4', 'qt5', 'svg', 'tk',
#     widget', 'wx']
#     Configure matplotlib for interactive use with the default matplotlib
#     backend.
# try:
#     import matplotlib
# except (ImportError, ModuleNotFoundError):
#     c.InteractiveShellApp.matplotlib = None
# else:
#     c.InteractiveShellApp.matplotlib = 'auto'

# Run the module as a script.
# c.InteractiveShellApp.module_to_run = ''

# Pre-load matplotlib and numpy for interactive use, selecting a particular
# matplotlib backend and loop integration.
# See matplotlib choices above:
# c.InteractiveShellApp.pylab = None

# If true, IPython will populate the user namespace with numpy, pylab, etc. and
#  an ``import *`` is done from numpy and pylab, when using pylab mode.
# Dude I never noticed that this defaults to True like whatttt
#  When False, pylab mode should not import any names into the user namespace.
# c.InteractiveShellApp.pylab_import_all = True
# Reraise exceptions encountered loading IPython extensions?
c.InteractiveShellApp.reraise_ipython_extension_failures = False

# ----------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ----------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
# Default: '%Y-%m-%d %H:%M:%S'
c.Application.log_datefmt = "%Y-%m-%d %H:%M:%S"

# The Logging format template
# Default: '[%(name)s]%(highlevel)s %(message)s'
# Todo: Import traitlets.config.application.LevelFormatter
c.Application.log_format = "%(module)s %(created)f [ %(name)s ] %(message)s"

# Set the log level by value or name.
c.Application.log_level = 20

# ----------------------------------------------------------------------------
# BaseIPythonApplication(Application) configuration
# ----------------------------------------------------------------------------

# IPython: an enhanced interactive Python shell.

# Whether to create profile dir if it doesn't exist
# c.BaseIPythonApplication.auto_create = False

# Whether to install the default config files into the profile dir. If a new
#  profile is being created, and IPython contains config files for that profile
#  then they will be staged into the new directory.  Otherwise, default config
#  files will be automatically generated.
# c.BaseIPythonApplication.copy_config_files = False

# Path to an extra config file to load.
#
#  If specified, load this config file in addition to any other IPython config.
# c.BaseIPythonApplication.extra_config_file = ''

# The name of the IPython directory. This directory is used for logging
# configuration (through profiles), history storage, etc. The default is
# usually $HOME/.ipython. This option can also be specified through the environment
# variable IPYTHONDIR.
if os.environ.get("IPYTHONDIR"):
    c.BaseIPythonApplication.ipython_dir = os.environ.get("IPYTHONDIR")
else:
    # Assume home was defined correctly up top. Will need to rewrite for windows
    c.BaseIPythonApplication.ipython_dir = os.path.join(home, ".ipython")

# Whether to overwrite existing config files when copying
# c.BaseIPythonApplication.overwrite = False

# The IPython profile to use.
c.BaseIPythonApplication.profile = "default"

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
c.TerminalIPythonApp.force_interact = False

# ---
# Class to use to instantiate the TerminalInteractiveShell object. Useful for
#  custom Frontends
# c.TerminalIPythonApp.interactive_shell_class =
# 'IPython.terminal.interactiveshell.TerminalInteractiveShell'

# Start IPython quickly by skipping the loading of config files.
# c.TerminalIPythonApp.quick = False

# Dec 08, 2019: Adding this in
c.TerminalIPythonApp.log_format = "%(module)s %(created)f [ %(name)s ]  %(message)s "

# Configure matplotlib for interactive use with the default matplotlib backend.

# TerminalIPythonApp.matplotlib=<CaselessStrEnum>
#     Default: None
#     Choices: ['auto', 'agg', 'gtk', 'gtk3', 'inline', 'ipympl', 'nbagg',
#     notebook', 'osx', 'pdf', 'ps', 'qt', 'qt4', 'qt5', 'svg', 'tk',
#     widget', 'wx']
#     Configure matplotlib for interactive use with the default matplotlib
#     backend.
try:
    import matplotlib
except (ImportError, ModuleNotFoundError):
    c.TerminalIPythonApp.matplotlib = None
except OSError:
    c.TerminalIPythonApp.matplotlib = None
except Exception as e:
    if getattr(sys, "exc_info", None):
        print(sys.exc_info()[2])
else:
    c.TerminalIPythonApp.matplotlib = "auto"
    # TODO: I accidentally set this as a config of InteractiveShellApp.
    # Was this why i've eeen having so many unexplainable mpl problems?
    # Why is this a problem and what causes it?
    # c.InteractiveShellApp.pylab = 'auto'

# ------------------------------------------------------------------------------
# InteractiveShell(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

# An enhanced, interactive shell for Python.

# AKA:  Make IPython automatically call any callable object even if you didn't type
# c.InteractiveShell.autocall = True

# A list of ast.NodeTransformer subclass instances, which will be applied to
#  user input before code is run.
# c.InteractiveShell.ast_transformers = []

# Automatically run await statement in the top level repl.
# Must be boolean. Where do we specify the runner?
if version_info > (7, 2):
    c.InteractiveShell.autoawait = True
else:
    c.InteractiveShell.autoawait = False

# Make IPython automatically call any callable object even if you didn't type
# explicit parentheses. For example, 'str 43' becomes 'str(43)' automatically.
# The value can be '0' to disable the feature, '1' for 'smart' autocall, where
# it is not applied if there are no more arguments on the line, and '2' for
# 'full' autocall, where all callable objects are automatically called (even if
# no arguments are present).
c.InteractiveShell.autocall = 0

# Autoindent IPython code entered interactively.
# Jupyter Console doesn't handle this correctly. Alledgedly ipy7.0 fixed that
# try:
#     c.InteractiveShell.autoindent = True
# except Exception:
#     pass

# Enable magic commands to be called without the leading %.
# c.InteractiveShell.automagic = True

# The part of the banner to be printed before the profile
c.InteractiveShell.banner1 = ""

# Let's try rewriting the banner.
# check IPython/core/usage.py
# unfortunately this doesn't work yet. release isn't defined and idk where
# they define it in the original file.
# rewritten_banner_parts = [
#     "Python %s\n" % sys.version.split("\n")[0],
#     "IPython {version} ".format(version=release.version),
# ]

#  rewritten_banner = ''.join(rewritten_banner_parts)

#  c.InteractiveShell.banner1 = rewritten_banner

# The part of the banner to be printed after the profile
c.InteractiveShell.banner2 = ""

# Set the size of the output cache. The default is 1000, you can change it
# permanently in your config file. Setting it to 0 completely disables the
# caching system, and the minimum value accepted is 3 (if you provide a value
# less than 3, it is reset to 0 and a warning is issued). This limit is defined
# because otherwise you'll spend more time re-flushing a too small cache than
# working
c.InteractiveShell.cache_size = 10000

# Use colors for displaying information about objects. Because this information
#  is passed through a pager (like 'less'), and some pagers get confused with
#  color codes, this capability can be turned off.
c.InteractiveShell.color_info = True

# Set the color scheme (NoColor, Neutral, Linux, or LightBG).
c.InteractiveShell.colors = "Linux"

c.InteractiveShell.debug = True

# Don't call post-execute functions that have failed in the past.
# c.InteractiveShell.disable_failing_post_execute = False

# If True, anything that would be passed to the pager will be displayed as
#  regular output instead.
# Only if we don't have bat.

if platform.system() == "Windows":
    c.InteractiveShell.display_page = True
else:
    if shutil.which("bat"):
        c.InteractiveShell.display_page = False

# (Provisional API) enables html representation in mime bundles sent to pagers.
# c.InteractiveShell.enable_html_pager = False

# Total length of command history
c.InteractiveShell.history_length = 50000

# The number of saved history entries to be loaded into the history buffer at
#  startup.
c.InteractiveShell.history_load_length = 10000

# c.InteractiveShell.ipython_dir = ''

# Start logging to the given file in append mode. Use `logfile` to specify a
# log file to **overwrite** logs to.
# c.InteractiveShell.logappend = ''

# The name of the logfile to use.
# c.InteractiveShell.logfile = ''

# Start logging to the default log file in overwrite mode. Use `logappend` to
#  specify a log file to **append** logs to.
# c.InteractiveShell.logstart = False

# NEW CODE WHOO
# Select the loop runner that will be used to execute top-level asynchronous
# code
# c.InteractiveShell.loop_runner = 'IPython.core.interactiveshell._asyncio_runner'
# c.InteractiveShell.loop_runner = None

# TODO: allow_none should be added to the loop runner. Check below tb

# File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/interactiveshell.py", line 402, in _import_runner
#     raise ValueError('loop_runner must be callable')

# ValueError: loop_runner must be callable

# TODO: What is this?

# --TerminalInteractiveShell.object_info_string_level=<Enum>
#     Default: 0
#     Choices: (0, 1, 2)
# c.InteractiveShell.object_info_string_level = 0

# Automatically call the pdb debugger after every exception.
# c.InteractiveShell.pdb = False

# from time import time
# Is the prompt manager class ignored? Yes!
# c.PromptManager.in_template = u"{color.LightGreen}{time}{color.Yellow} {color.normal}>>>"
# Deprecated since IPython 4.0 and ignored since 5.0, set
# TerminalInteractiveShell.prompts object directly.
# c.InteractiveShell.prompt_in1 = 'In [\\#]: '

# Deprecated since IPython 4.0 and ignored since 5.0, set
# TerminalInteractiveShell.prompts object directly.
# c.InteractiveShell.prompt_in2 = '   .\\D.: '

# Deprecated since IPython 4.0 and ignored since 5.0, set
# TerminalInteractiveShell.prompts object directly.
# c.InteractiveShell.prompt_out = 'Out[\\#]: '

# Deprecated since IPython 4.0 and ignored since 5.0, set
# TerminalInteractiveShell.prompts object directly.
# c.InteractiveShell.prompts_pad_left = True

c.InteractiveShell.quiet = False

# c.InteractiveShell.separate_in = '\n'

# c.InteractiveShell.separate_out = ''

# c.InteractiveShell.separate_out2 = ''

# Show rewritten input, e.g. for autocall.
# c.InteractiveShell.show_rewritten_input = True

# Jan 20, 2019: Even with docrepr installed this still ends up raising errors.
# Need to debug later.
# c.InteractiveShell.sphinxify_docstring = False
#  module).
# c.InteractiveShell.separate_out2 = ''

# Jan 20, 2019: Even with docrepr installed this still ends up raising errors.
# Need to debug later.
# c.InteractiveShell.sphinxify_docstring = False
#  module).

c.InteractiveShell.wildcards_case_sensitive = False

# Switch modes for the IPython exception handlers.
# Default: 'Context'
# Choices: ['Context', 'Plain', 'Verbose', 'Minimal']
# c.InteractiveShell.xmode = 'Context'

# ----------------------------------------------------------------------------
# TerminalInteractiveShell(InteractiveShell) configuration
# ----------------------------------------------------------------------------

# 'all', 'last', 'last_expr' or 'none', 'last_expr_or_assign' specifying which
#  nodes should be run interactively (displaying output from expressions).
c.TerminalInteractiveShell.ast_node_interactivity = "last_expr_or_assign"

# Autoformatter to reformat Terminal code. Can be `'black'` or `None`
c.TerminalInteractiveShell.autoformatter = None

# Set to confirm when you try to exit IPython with an EOF (Control-D in Unix,
#  Control-Z/Enter in Windows). By typing 'exit' or 'quit', you can force a
#  direct exit without any confirmation.
c.TerminalInteractiveShell.confirm_exit = False

# Options for displaying tab completions, 'column', 'multicolumn', and
#  'readlinelike'. These options are for `prompt_toolkit`, see `prompt_toolkit`
#  documentation for more information.
c.TerminalInteractiveShell.display_completions = "multicolumn"

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
    else:
        c.TerminalInteractiveShell.editing_mode = "emacs"

# TODO: What is the API for traitlets.LazyConfigValue? It doesn't have a log method.
# c.log("Editing Mode:\t {!s}".format(c.TerminalInteractiveShell.editing_mode))

# Set the editor used by IPython (default to $EDITOR/vi/notepad).
c.TerminalInteractiveShell.editor = "nvim"

# Allows to enable/disable the prompt toolkit history search
# c.TerminalInteractiveShell.enable_history_search = True

# Enable vi (v) or Emacs (C-X C-E) shortcuts to open an external editor.
# This is in addition to the F2 binding, which is always enabled.
c.TerminalInteractiveShell.extra_open_editor_shortcuts = True

# Provide an alternative handler to be called when the user presses Return.
# This is an advanced option intended for debugging, which may be changed or
# removed in later releases.
# Wth no it's not? It's a feature not something that should be subject to removal.
# c.TerminalInteractiveShell.handle_return = None

# Highlight matching brackets.
# c.TerminalInteractiveShell.highlight_matching_brackets = True

# The name or class of a Pygments style to use for syntax highlighting.
# To see available styles, run `pygmentize -L styles`.
# c.TerminalInteractiveShell.highlighting_style = traitlets.Undefined

# default, emacs, friendly, colorful, autumn, murphy, manni, monokai, perldoc,
# pastie, borland, trac, native, fruity, bw, vim, vs, tango, rrt, xcode, igor,
# paraiso-light, paraiso-dark, lovelace, algol, algol_nu, arduino, rainbow_dash

# Try to import my Gruvbox class. Can be found at
# https://github.com/farisachugthai/Gruvbox_IPython

if platform.system() == "Windows":
    from pygments.styles.friendly import FriendlyStyle

    # I know it's odd making this platform specific but everything is completely illegible otherwise
    c.TerminalInteractiveShell.highlighting_style = "friendly"
else:
    try:
        from gruvbox.style import GruvboxDarkHard
    except (ImportError, ModuleNotFoundError):
        from pygments.styles.friendly import FriendlyStyle

        c.TerminalInteractiveShell.highlighting_style = "friendly"

    else:
        c.TerminalInteractiveShell.highlighting_style = "GruvboxDarkHard"


def get_env():
    """Would it make sense to combine functools.lru_cache with this?"""
    return os.environ.copy()


environment = get_env()
if "LESS" not in environment:
    # nah you set this var wrong
    # os.environ.setdefault("LESS", "JRKMLigeF")
    os.environ.setdefault("LESSHISTSIZE", "5000")

if "LESS_TERMCAP_mb" not in environment:
    # Who is curios as to whether this is gonna work or not?
    os.environ.setdefault("LESS_TERMCAP_mb", r"\e[01;31m")
    os.environ.setdefault("LESS_TERMCAP_md", r"\e[01;38;5;180m")
    os.environ.setdefault("LESS_TERMCAP_me", r"\e[0m")
    os.environ.setdefault("LESS_TERMCAP_se", r"\e[0m")
    os.environ.setdefault("LESS_TERMCAP_so", r"\e[03;38;5;202m")
    os.environ.setdefault("LESS_TERMCAP_ue", r"\e[0m")
    os.environ.setdefault("LESS_TERMCAP_us", r"\e[04;38;5;139m")

# Override highlighting format for specific tokens
# Comments were genuinely impossible to read. Might need to override
# punctuation next.
# c.TerminalInteractiveShell.highlighting_style_overrides = {Comment: '#ffffff'}

# No help docs? Update when you find the sauce
# c.TerminalInteractiveShell.mime_renderers = {}

# Enable mouse support in the prompt (Note: prevents selecting text with the
# mouse)
# c.TerminalInteractiveShell.mouse_support = False

# Class used to generate Prompt token for prompt_toolkit
# So this wouldn't be a block of code to build off of but here's something
# so you can get an idea of what's going on


class StandardPythonPrompt(ClassicPrompts):
    """Create a no-op class to demonstrate usage of the ClassicPrompts class.

    Examples
    --------
    >>> from IPython.terminal.prompts import ClassicPrompts
    >>> from IPython.core.getipython import get_ipython
    >>> ClassicPrompts(get_ipython()).continuation_prompt_tokens()
    [(Token.Prompt, '... ')]
    >>> ClassicPrompts(get_ipython()).continuation_prompt_tokens()
    [(Token.Prompt, '>>> ')]

    """

    def __repr__(self):
        """The most boiler-platey repr I can come up with."""
        return self.__class__.__name__

        # def __call__(self):
        """TODO"""
        # return


# As an aside I believe that this attr is the same as Prompt
# c.TerminalInteractiveShell.prompts_class = 'IPython.terminal.prompts.Prompts'

# Use `raw_input` for the REPL, without completion and prompt colors.

# Useful when controlling IPython as a subprocess, and piping STDIN/OUT/ERR.
# Known usage are: IPython own testing machinery, and emacs inferior-shell
# integration through elpy.

# This mode default to `True` if the `IPY_TEST_SIMPLE_PROMPT` environment
# variable is set, or the current terminal is not a tty.
# c.TerminalInteractiveShell.simple_prompt = False

# Number of line at the bottom of the screen to reserve for the completion menu
c.TerminalInteractiveShell.space_for_menu = 6

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

# *****************************************************************************
# What this implies is that if you want to create your own tool for analyzing
# your history logs in IPython, start here!
# *****************************************************************************

# Options for configuring the SQLite connection

# These options are passed as keyword args to sqlite3.connect when establishing
#  database connections.
# c.HistoryAccessor.connection_options = {}

# enable the SQLite history

# set enabled=False to disable the SQLite history, in which case there will be
# no stored history, no SQLite connection, and no background saving thread.
# This may be necessary in some threaded environments where IPython is embedded.
# c.HistoryAccessor.enabled = True

# Path to file to use for SQLite history database.

# By default, IPython will put the history database in the IPython profile
# directory.  If you would rather share one history among profiles, you can set
# this value in each, so that they are consistent.

# Due to an issue with fcntl, SQLite is known to misbehave on some NFS mounts.
# If you see IPython hanging, try setting this to something on a local disk,
# e.g::

#      ipython --HistoryManager.hist_file=/tmp/ipython_hist.sqlite

# you can also use the specific value `:memory:` (including the colon at both
# end but not the back ticks), to avoid creating an history file.

# Wait a second that's how prompt_toolkit does it! Does the base class inherit
# from :class:`prompt_toolkit.history.History`
# c.HistoryAccessor.hist_file = ''

# ----------------------------------------------------------------------------
# HistoryManager(HistoryAccessor) configuration
# ----------------------------------------------------------------------------

# HistoryManager.connection_options=<Dict>
# Default: {}

# Options for configuring the SQLite connection
# These options are passed as keyword args to sqlite3.connect when
# establishing database connections.
# A class to organize all history-related functionality in one place.
# c.HistoryManager.connection_options={}

# Write to database every x commands (higher values save disk access & power).
# Values of 1 or less effectively disable caching.
c.HistoryManager.db_cache_size = 16

# Should the history database include output? (default: no)
c.HistoryManager.db_log_output = True

# ----------------------------------------------------------------------------
# ProfileDir(LoggingConfigurable) configuration
# ----------------------------------------------------------------------------

# An object to manage the profile directory and its resources.

#  The profile directory is used by all IPython applications, to manage
#  configuration, logging and security.

#  This object knows how to find, create and manage these directories. This
#  should be used by any code that wants to handle profiles.
# c.ProfileDir.location = ''

# Set the profile location directly. This overrides the logic used by the
#  `profile` option.

# 05/18/19: I'm enabling this as it overrides the logic used for profile in
# the `BaseIPythonApplication` section
c.ProfileDir.location = os.path.join(home, "", ".ipython")

# ----------------------------------------------------------------------------
# BaseFormatter(Configurable) configuration
# ----------------------------------------------------------------------------


class BaseFormatterDoc(Configurable):
    """A base formatter class that is configurable.

    This formatter should usually be used as the base class of all formatters. It
    is a traited :class:`Configurable` class and includes an extensible API for
    users to determine how their objects are formatted. The following logic is
    used to find a function to format an given object.

    1. The object is introspected to see if it has a method with the name
    :attr:`print_method`. If is does, that object is passed to that method
    for formatting.
    2. If no print method is found, three internal dictionaries are consulted
    to find print method: :attr:`singleton_printers`, :attr:`type_printers`
    and :attr:`deferred_printers`.

    Users should use these dictionaries to register functions that will be used
    to compute the format data for their objects (if those objects don't have the
    special print methods). The easiest way of using these dictionaries is
    through the :meth:`for_type` and :meth:`for_type_by_name` methods.

    If no function/callable is found to compute the format data, ``None`` is
    returned and this format type is not used.

    .. seealso:: :mod:`IPython.lib.pretty`.

    """

    def __init__(self, *args, **kwargs):
        """Initialize a BaseFormatter and get some Sphinx help.

        The remaining attributes from the config file are::

            c.BaseFormatter.deferred_printers = {}

            c.BaseFormatter.enabled = True

            c.BaseFormatter.singleton_printers = {}

            c.BaseFormatter.type_printers = {}

        """
        super().__init__(*args, **kwargs)

    def _example_subclass(self):
        """
        PlainTextFormatter(BaseFormatter) configuration
        -----------------------------------------------

        The default pretty-printer.

        This uses :mod:`IPython.lib.pretty` to compute the format data of
        the object.

        If the object cannot be pretty printed, :func:`repr` is used.

        See the documentation of :mod:`IPython.lib.pretty` for details on
        how to write pretty printers.  Here is a simple example::

            def dtype_pprinter(obj, p, cycle):
                if cycle:
                    return p.text('dtype(...)')
                if hasattr(obj, 'fields'):
                    if obj.fields is None:
                        p.text(repr(obj))
                    else:
                        p.begin_group(7, 'dtype([')
                        for i, field in enumerate(obj.descr):
                            if i > 0:
                                p.text(',')
                                p.breakable()
                            p.pretty(field)
                        p.end_group(7, '])')

        c.PlainTextFormatter.float_precision = ''

        Truncate large collections (lists, dicts, tuples, sets) to this size.

        Set to 0 to disable truncation.
        Default is 1000 but that floods a terminal.
        c.PlainTextFormatter.max_seq_length = 100

        Default value
        c.PlainTextFormatter.max_width = 79

        c.PlainTextFormatter.newline = '\n'

        c.PlainTextFormatter.pprint = True

        c.PlainTextFormatter.verbose = True
        """
        return repr(self.__doc__)

    def __repr__(self):
        return self._example_subclass()


# ----------------------------------------------------------------------------
# Completer(Configurable) configuration
# ----------------------------------------------------------------------------

# Enable unicode completions, e.g. \alpha<tab> . Includes completion of latex
#  commands, unicode names, and expanding unicode characters back to latex
#  commands.
# c.Completer.backslash_combining_completions = True

# Enable debug for the Completer. Mostly print extra information for
#  experimental jedi integration.
c.Completer.debug = False

# Activate greedy completion PENDING DEPRECTION. this is now mostly taken care
#  of with Jedi.
#
#  This will enable completion on elements of lists, results of function calls,
#  etc., but can be unsafe because the code is actually evaluated on TAB.
# c.Completer.greedy = False

# Experimental: restrict time (in milliseconds) during which Jedi can compute
#  types. Set to 0 to stop computing types. Non-zero value lower than 100ms may
#  hurt performance by preventing jedi to build its cache.
c.Completer.jedi_compute_type_timeout = 0

# Experimental: Use Jedi to generate autocompletions. Default to True if jedi
# is installed
# try:
#     import jedi
# except ImportError:  # clearly not installed
c.Completer.use_jedi = False
# else:
#     c.Completer.use_jedi = True

# It's not that I don't want to use jedi, it's that our implementation is awful

# ----------------------------------------------------------------------------
# IPCompleter(Completer) configuration
# ----------------------------------------------------------------------------

# Extension of the completer class with IPython-specific features

# DEPRECATED as of version 5.0.
#
#  Instruct the completer to use __all__ for the completion
#
#  Specifically, when completing on ``object.<tab>``.
#
#  When True: only those names in obj.__all__ will be included.
#
#  When False [default]: the __all__ attribute is ignored
# c.IPCompleter.limit_to__all__ = False

# Whether to merge completion results into a single list
#
# If False, only the completion results from the first non-empty completer will
# be returned.
# c.IPCompleter.merge_completions = True

# Instruct the completer to omit private method names
#  Specifically, when completing on ``object.<tab>``.
#  When 2 [default]: all names that start with '_' will be excluded.
#  When 1: all 'magic' names (``__foo__``) will be excluded.
#  When 0: nothing will be excluded.
c.IPCompleter.omit__names = 1

# ----------------------------------------------------------------------------
# ScriptMagics(Magics) configuration
# ----------------------------------------------------------------------------

# Magics for talking to scripts
# This defines a base `%%script` cell magic for running a cell with a program
# in a subprocess, and registers a few top-level magics that call %%script with
# common interpreters.

# Extra script cell magics to define
# This generates simple wrappers of `%%script foo` as `%%foo`.
#
# If you want to add script magics that aren't on your path, specify them in
# script_paths
# c.ScriptMagics.script_magics = []

# Dict mapping short 'ruby' names to full paths, such as '/opt/secret/bin/ruby'
# Only necessary for items in script_magics where the default path will not
# find the right interpreter.
# c.ScriptMagics.script_paths = {}

# ----------------------------------------------------------------------------
# LoggingMagics(Magics) configuration
# ----------------------------------------------------------------------------

# Magics related to all logging machinery.
# Suppress output of log state when logging is enabled
c.LoggingMagics.quiet = True

# ----------------------------------------------------------------------------
# StoreMagics(Magics) configuration
# ----------------------------------------------------------------------------

# Lightweight persistence for python variables.
# Provides the %store magic.
# If True, any %store-d variables will be automatically restored when IPython
# starts.
c.StoreMagics.autorestore = False
