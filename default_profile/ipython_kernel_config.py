#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration file for ipython-kernel."""
import logging
import os
from pathlib import Path
from platform import platform

from traitlets.config import get_config
from IPython.core.getipython import get_ipython
# even if we're not using them now we will
from ipykernel.ipkernel import IPythonKernel, ZMQInteractiveShell   # noqa
from ipykernel.zmqshell import ZMQShellDisplayHook
from zmq.backend.cython.context import Context

c = get_config()  # noqa

context = Context()


def instantiate_kernel_logger():
    kernel_logger = logging.getLogger(name=__name__)
    log_datefmt = "%Y-%m-%d %H:%M:%S"
    BASIC_FORMAT = "[%(created)f %(levelname)s ] %(module)s  %(message)s : "
    kernel_formatter = logging.Formatter(fmt=BASIC_FORMAT, datefmt=log_datefmt)
    kernel_logger.handlers = []
    handler = logging.StreamHandler()
    handler.setFormatter(kernel_formatter)
    handler.setLevel(logging.WARNING)
    kernel_logger.addHandler(handler)
    kernel_logger.setLevel(logging.WARNING)
    return kernel_logger


logger = instantiate_kernel_logger()


def get_home():
    """Return :func:`pathlib.Path.home`."""
    return Path.home()


# -----------------------------------------------------------------------------
# BaseIPythonApplication(Application) configuration
# -----------------------------------------------------------------------------

# The name of the IPython directory. This directory is used for logging
# configuration (through profiles), history storage, etc. The default is
# usually $HOME/.ipython. This option can also be specified through the environment
# variable IPYTHONDIR.
if os.environ.get("IPYTHONDIR"):
    c.BaseIPythonApplication.ipython_dir = os.environ.get("IPYTHONDIR")
else:
    # Assume home was defined correctly up top. Will need to rewrite for windows
    c.BaseIPythonApplication.ipython_dir = os.path.join(get_home(), ".ipython")

# Whether to overwrite existing config files when copying
# c.BaseIPythonApplication.overwrite = False

# The IPython profile to use.
# c.BaseIPythonApplication.profile = 'default'

# Create a massive crash report when IPython encounters what may be an internal
# error.  The default is to append a short message to the usual traceback
# c.BaseIPythonApplication.verbose_crash = False

# -----------------------------------------------------------------------------
# IPKernelApp(BaseIPythonApplication,InteractiveShellApp,ConnectionFileMixin)
# configuration
# -----------------------------------------------------------------------------

# IPython: an enhanced interactive Python shell.

# The importstring for the DisplayHook factory
shell = get_ipython()
if shell is not None:
    zmq_display_hook = ZMQShellDisplayHook(shell)
    c.IPKernelApp.displayhook_class = zmq_display_hook
    # 'ipykernel.displayhook.ZMQDisplayHook'

cur_platform = platform()
if cur_platform.startswith("Win"):
    c.IPKernelApp.interrupt = 1

# The Kernel subclass to be used.
#
# This should allow easy re-use of the IPKernelApp entry point to configure and
# launch kernels other than IPython's own.
# c.IPKernelApp.kernel_class = 'ipykernel.ipkernel.IPythonKernel'

# redirect stderr to the null device
# c.IPKernelApp.no_stderr = False

# redirect stdout to the null device
# c.IPKernelApp.no_stdout = False

# The importstring for the OutStream factory
# c.IPKernelApp.outstream_class = 'ipykernel.iostream.OutStream'

# kill this process if its parent dies.  On Windows, the argument specifies the
# HANDLE of the parent process, otherwise it is simply boolean.
# c.IPKernelApp.parent_handle = 0

# Only send stdout/stderr to output stream
c.IPKernelApp.quiet = False

# -----------------------------------------------------------------------------
# Kernel(SingletonConfigurable) configuration
# -----------------------------------------------------------------------------

# Whether to use appnope for compatiblity with OS X App Nap.
#
# Only affects OS X >= 10.9.
# c.Kernel._darwin_app_nap = True

# c.Kernel._execute_sleep = 0.0005

# c.Kernel._poll_interval = 0.05

# time (in seconds) to wait for messages to arrive when aborting queued requests
# after an error.
# Requests that arrive within this window after an error will be cancelled.

# Increase in the event of unusually slow network causing significant delays,
# which can manifest as e.g. "Run all" in a notebook aborting some, but not all,
# messages after an error.
# c.Kernel.stop_on_error_timeout = 0.1

# -----------------------------------------------------------------------------
# IPythonKernel(Kernel) configuration
# -----------------------------------------------------------------------------

c.IPythonKernel.help_links = [
    {
        "text": "pandas Reference",
        "url": "https://pandas.pydata.org/pandas-docs/stable/",
    },
    {"text": "IPython Reference", "url": "https://ipython.org/documentation.html"},
    {"text": "NumPy Reference", "url": "https://docs.scipy.org/doc/numpy/reference/"},
    {"text": "SciPy Reference", "url": "https://docs.scipy.org/doc/scipy/reference/"},
    {"text": "Matplotlib Reference", "url": "https://matplotlib.org/contents.html"},
    {"text": "SymPy Reference", "url": "http://docs.sympy.org/latest/index.html"},
]

# Set this flag to False to deactivate the use of experimental IPython
# completion APIs.
c.IPythonKernel.use_experimental_completions = False

# -----------------------------------------------------------------------------
# InteractiveShell(SingletonConfigurable) configuration
# -----------------------------------------------------------------------------

# An enhanced, interactive shell for Python.

# 'all', 'last', 'last_expr' or 'none', 'last_expr_or_assign' specifying which
# nodes should be run interactively (displaying output from expressions).

try:
    c.InteractiveShell.ast_node_interactivity = "last_expr_or_assign"
except:
    c.InteractiveShell.ast_node_interactivity = "last_expr"


# A list of ast.NodeTransformer subclass instances, which will be applied to
# user input before code is run.
# c.InteractiveShell.ast_transformers = []

# Automatically run await statement in the top level repl.
if cur_platform.startswith("Win"):
    c.InteractiveShell.autoawait = False
else:
    c.InteractiveShell.autoawait = True

# Make IPython automatically call any callable object even if you didn't type
# explicit parentheses. For example, 'str 43' becomes 'str(43)' automatically.
# The value can be '0' to disable the feature, '1' for 'smart' autocall, where
# it is not applied if there are no more arguments on the line, and '2' for
# 'full' autocall, where all callable objects are automatically called (even if
# no arguments are present).
# c.InteractiveShell.autocall = 0

# Enable magic commands to be called without the leading %.
c.InteractiveShell.automagic = True

# The part of the banner to be printed before the profile
# Stop being so noisy like goddamn
c.InteractiveShell.banner1 = ""

# The part of the banner to be printed after the profile
# c.InteractiveShell.banner2 = ''

# Set the size of the output cache.  The default is 1000, you can change it
# permanently in your config file.  Setting it to 0 completely disables the
# caching system, and the minimum value accepted is 3 (if you provide a value
# less than 3, it is reset to 0 and a warning is issued).

# This limit is defined because otherwise you'll spend more time
# re-flushing a too small cache than working
c.InteractiveShell.cache_size = 1000

# Use colors for displaying information about objects. Because this information
# is passed through a pager (like 'less'), and some pagers get confused with
# color codes, this capability can be turned off.
# c.InteractiveShell.color_info = True

# Set the color scheme (NoColor, Neutral, Linux, or LightBG).
c.InteractiveShell.colors = "Linux"

c.InteractiveShell.debug = True

# Don't call post-execute functions that have failed in the past.
# c.InteractiveShell.disable_failing_post_execute = False

# If True, anything that would be passed to the pager will be displayed as
# regular output instead.
# c.InteractiveShell.display_page = True

# (Provisional API) enables html representation in mime bundles sent to pagers.
c.InteractiveShell.enable_html_pager = False

# Total length of command history
c.InteractiveShell.history_length = 1000

# The number of saved history entries to be loaded into the history buffer at
# startup.
c.InteractiveShell.history_load_length = 100

c.InteractiveShell.ipython_dir = str(get_home().joinpath(".ipython"))

# Start logging to the given file in append mode. Use `logfile` to
# specify a log file to **overwrite** logs to.
# c.InteractiveShell.logappend = ''

# The name of the logfile to use.
# c.InteractiveShell.logfile = ''

# Start logging to the default log file in overwrite mode. Use `logappend` to
# specify a log file to **append** logs to.
# c.InteractiveShell.logstart = False

# Not allowed to do this :/
# c.InteractiveShell.loop_runner = None

# Automatically call the pdb debugger after every exception.
# c.InteractiveShell.pdb = False

# Show rewritten input, e.g. for autocall.
# c.InteractiveShell.show_rewritten_input = True

# Enables rich html representation of docstrings. (This requires the docrepr
# module).
c.InteractiveShell.sphinxify_docstring = False

# c.InteractiveShell.wildcards_case_sensitive = False

# Switch modes for the IPython exception handlers.
c.InteractiveShell.xmode = "Verbose"

# -----------------------------------------------------------------------------
# ZMQInteractiveShell(InteractiveShell) configuration
# -----------------------------------------------------------------------------

# A subclass of InteractiveShell for ZMQ.

# -----------------------------------------------------------------------------
# ProfileDir(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------

# An object to manage the profile directory and its resources.
#
# The profile directory is used by all IPython applications, to manage
# configuration, logging and security.
#
# This object knows how to find, create and manage these directories. This
# should be used by any code that wants to handle profiles.

# Set the profile location directly. This overrides the logic used by the
# `profile` option.
if os.environ.get("IPYTHONDIR"):
    c.ProfileDir.location = os.environ.get("IPYTHONDIR")
else:
    if get_home():
        c.ProfileDir.location = Path.joinpath(get_home(), "", ".ipython")

# -----------------------------------------------------------------------------
# Session(Configurable) configuration
# -----------------------------------------------------------------------------

# Object for handling serialization and sending of messages.
#
# The Session object handles building messages and sending them with ZMQ
# sockets or ZMQStream objects.  Objects can communicate with each other
# over the network via Session objects, and only need to work with the
# dict - based IPython message spec. The Session will handle
# serialization/deserialization, security, and metadata.

# Sessions support configurable serialization via packer/unpacker traits, and
# signing with HMAC digests via the key/keyfile traits.

# Parameters ----------

# debug : bool
#     whether to trigger extra debugging statements
# packer/unpacker : str : 'json', 'pickle' or import_string
#     importstrings for methods to serialize message parts.  If just
#     'json' or 'pickle', predefined JSON and pickle packers will be used.
#     Otherwise, the entire importstring must be used.
#
#     The functions must accept at least valid JSON input, and output *bytes*.
#
#     For example, to use msgpack:
#     packer = 'msgpack.packb', unpacker='msgpack.unpackb'
# pack/unpack : callables
#     You can also set the pack/unpack callables for serialization directly.
# session : bytes
#     the ID of this Session object.  The default is to generate a new UUID.
# username : unicode
#     username added to message headers.  The default is to ask the OS.
# key : bytes
#     The key used to initialize an HMAC signature.  If unset, messages
#     will not be signed or checked.
# keyfile : filepath
#     The file containing a key.  If this is set, `key` will be initialized
#     to the contents of the file.

# Threshold (in bytes) beyond which an object's buffer should be extracted to
# avoid pickling.
# c.Session.buffer_threshold = 1024

# Whether to check PID to protect against calls after fork.
#
# This check can be disabled if fork-safety is handled elsewhere.
# c.Session.check_pid = True

# Threshold (in bytes) beyond which a buffer should be sent without copying.
# c.Session.copy_threshold = 65536

# Debug output in the Session
# c.Session.debug = False

# The maximum number of digests to remember.
#
# The digest history will be culled when it exceeds this value.
# c.Session.digest_history_size = 65536

# The maximum number of items for a container to be introspected for custom
# serialization. Containers larger than this are pickled outright.
# c.Session.item_threshold = 64

# execution key, for signing messages.
# c.Session.key = b''

# path to file containing execution key.
# c.Session.keyfile = ''

# Metadata dictionary, which serves as the default top-level metadata dict for
# each message.
# c.Session.metadata = {}

# The name of the packer for serializing messages. Should be one of 'json',
# 'pickle', or an import name for a custom callable serializer.
# c.Session.packer = 'json'

# The UUID identifying this session.
# c.Session.session = ''

# The digest scheme used to construct the message signatures. Must have the
# form 'hmac-HASH'.
# c.Session.signature_scheme = 'hmac-sha256'

# The name of the unpacker for unserializing messages. Only used with custom
# functions for `packer`.
# c.Session.unpacker = 'json'

# Username for the Session. Default is your system username.
c.Session.username = "faris"
